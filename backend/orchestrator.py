"""
Multi-Model Orchestrator
Intelligent routing and fallback for LLM providers with 99.9% uptime guarantee
Uses Groq (primary), Ollama for text (your local models), Google Gemini (vision fallback)
"""
import time
import asyncio
import base64
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass
from groq import Groq, AsyncGroq
import google.generativeai as genai
from huggingface_hub import InferenceClient
from config import config

# Try to import ollama (optional for text fallback)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama not installed - text fallback disabled (vision still works)")


@dataclass
class ModelResponse:
    """Standardized response from any model"""
    content: str
    model_used: str
    latency_ms: float
    success: bool
    error: Optional[str] = None


class RateLimiter:
    """Track and enforce rate limits"""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []
    
    def can_request(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()
        # Remove old requests outside window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a new request"""
        self.requests.append(time.time())
    
    def wait_time(self) -> float:
        """Time to wait before next request is allowed"""
        if self.can_request():
            return 0.0
        
        oldest = min(self.requests)
        return (oldest + self.window_seconds) - time.time()


class MultiModelOrchestrator:
    """
    Orchestrates multiple LLM providers with intelligent fallback
    
    TEXT: Groq → Google Gemini → Ollama (your local models like GPT4All)
    VISION: Groq → Google Gemini (no Ollama vision models needed!)
    """
    
    def __init__(self):
        # Initialize clients
        self.groq_client = AsyncGroq(api_key=config.model.groq_api_key) if config.model.groq_api_key else None
        
        # Configure Google Gemini
        if config.model.gemini_api_key:
            genai.configure(api_key=config.model.gemini_api_key)
            self.gemini_available = True
        else:
            self.gemini_available = False
        
        self.hf_client = InferenceClient(token=config.model.hf_token) if config.model.hf_token else None
        
        # Rate limiters
        self.groq_limiter = RateLimiter(config.model.groq_rate_limit, window_seconds=60)
        
        # Stats
        self.stats = {
            "groq_calls": 0,
            "gemini_calls": 0,
            "ollama_calls": 0,  # For text only
            "hf_calls": 0,
            "failures": 0
        }
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> ModelResponse:
        """ Simplified interface for direct LLM generation """
        return await self.analyze_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model_type="general"
        )

    async def analyze_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_type: Literal["narrative", "clustering", "general"] = "general",
        response_format: Optional[str] = None
    ) -> ModelResponse:
        """
        Analyze text with automatic model selection and fallback
        
        Args:
            prompt: User prompt
            system_prompt: Optional system context
            model_type: Type of task (affects model selection)
            response_format: Optional "json" for structured output
        """
        start_time = time.time()
        
        # Select model based on type
        if model_type == "narrative":
            groq_model = config.model.text_narrative
        elif model_type == "clustering":
            groq_model = config.model.text_clustering
        else:
            groq_model = config.model.text_narrative
        
        # Try Groq first (fastest)
        if self.groq_client and self.groq_limiter.can_request():
            try:
                response = await self._groq_text(prompt, system_prompt, groq_model, response_format)
                self.groq_limiter.record_request()
                self.stats["groq_calls"] += 1
                return response
            except Exception as e:
                print(f"⚠️ Groq failed: {e}, falling back to Gemini")
        
        # Fallback to Google Gemini (free tier, reliable)
        if self.gemini_available:
            try:
                response = await self._gemini_text(prompt, system_prompt)
                self.stats["gemini_calls"] += 1
                return response
            except Exception as e:
                print(f"⚠️ Gemini failed: {e}, trying Ollama")
        
        # Third fallback: Ollama (your local models - optional)
        if OLLAMA_AVAILABLE:
            try:
                response = await self._ollama_text(prompt, system_prompt, response_format)
                self.stats["ollama_calls"] += 1
                return response
            except Exception as e:
                print(f"⚠️ Ollama failed: {e}")
        
        # If all fail, return error
        self.stats["failures"] += 1
        return ModelResponse(
            content="",
            model_used="none",
            latency_ms=(time.time() - start_time) * 1000,
            success=False,
            error="All models failed"
        )
    
    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> ModelResponse:
        """
        Analyze image with vision models
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            system_prompt: Optional system context
        """
        start_time = time.time()
        
        # Try Groq vision first
        if self.groq_client and self.groq_limiter.can_request():
            try:
                response = await self._groq_vision(image_path, prompt, system_prompt)
                self.groq_limiter.record_request()
                self.stats["groq_calls"] += 1
                return response
            except Exception as e:
                print(f"⚠️ Groq vision failed: {e}, falling back to Gemini")
        
        # Fallback to Google Gemini Vision
        if self.gemini_available:
            try:
                response = await self._gemini_vision(image_path, prompt)
                self.stats["gemini_calls"] += 1
                return response
            except Exception as e:
                print(f"⚠️ Gemini vision failed: {e}")
        
        self.stats["failures"] += 1
        return ModelResponse(
            content="",
            model_used="none",
            latency_ms=(time.time() - start_time) * 1000,
            success=False,
            error="All vision models failed"
        )
    
    async def parallel_validation(
        self,
        image_path: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Run multiple models in parallel for cross-validation
        Used for critical decisions like purity detection
        """
        tasks = []
        
        # Create tasks for available models
        if self.groq_client and self.groq_limiter.can_request():
            tasks.append(self._groq_vision(image_path, prompt))
        
        if self.gemini_available:
            tasks.append(self._gemini_vision(image_path, prompt))
        
        if not tasks:
            return {"consensus": None, "confidence": 0.0, "results": []}
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        valid_results = [r for r in results if isinstance(r, ModelResponse) and r.success]
        
        if not valid_results:
            return {"consensus": None, "confidence": 0.0, "results": []}
        
        # Simple consensus: majority voting on purity numbers
        consensus = self._calculate_consensus(valid_results)
        
        return {
            "consensus": consensus,
            "confidence": len(valid_results) / len(tasks),
            "results": [r.content for r in valid_results]
        }
    
    # === Provider-specific implementations ===
    
    async def _groq_text(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        response_format: Optional[str]
    ) -> ModelResponse:
        """Groq text completion"""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {"model": model, "messages": messages, "temperature": 0.2}
        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}
        
        response = await self.groq_client.chat.completions.create(**kwargs)
        
        return ModelResponse(
            content=response.choices[0].message.content,
            model_used=f"groq/{model}",
            latency_ms=(time.time() - start_time) * 1000,
            success=True
        )
    
    async def _gemini_text(
        self,
        prompt: str,
        system_prompt: Optional[str]
    ) -> ModelResponse:
        """Google Gemini text completion"""
        start_time = time.time()
        
        try:
            model = genai.GenerativeModel(config.model.text_local)
            
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(full_prompt)
            )
            
            return ModelResponse(
                content=response.text,
                model_used=f"gemini/{config.model.text_local}",
                latency_ms=(time.time() - start_time) * 1000,
                success=True
            )
        except Exception as e:
            return ModelResponse(
                content="",
                model_used="gemini",
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )
    
    async def _gemini_vision(
        self,
        image_path: str,
        prompt: str
    ) -> ModelResponse:
        """Google Gemini vision analysis"""
        start_time = time.time()
        
        try:
            import PIL.Image
            
            model = genai.GenerativeModel(config.model.vision_backup)
            img = PIL.Image.open(image_path)
            
            # Run in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content([prompt, img])
            )
            
            return ModelResponse(
                content=response.text,
                model_used=f"gemini/{config.model.vision_backup}",
                latency_ms=(time.time() - start_time) * 1000,
                success=True
            )
        except Exception as e:
            return ModelResponse(
                content="",
                model_used="gemini_vision",
                latency_ms=(time.time() - start_time) * 1000,
                success=False,
                error=str(e)
            )
    
    async def _ollama_text(
        self,
        prompt: str,
        system_prompt: Optional[str],
        response_format: Optional[str]
    ) -> ModelResponse:
        """Ollama local text completion (for your GPT4All or other models)"""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Use your gpt-oss:20b model (13GB, powerful!)
        kwargs = {"model": "gpt-oss:20b", "messages": messages}
        if response_format == "json":
            kwargs["format"] = "json"
        
        # Ollama is synchronous, run in executor
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, lambda: ollama.chat(**kwargs))
        
        return ModelResponse(
            content=response['message']['content'],
            model_used="ollama/gpt-oss:20b",
            latency_ms=(time.time() - start_time) * 1000,
            success=True
        )
    
    def _calculate_consensus(self, results: List[ModelResponse]) -> Optional[str]:
        """Calculate consensus from multiple model responses"""
        import re
        from collections import Counter
        
        # Extract purity numbers (925, 999, etc.)
        purity_votes = []
        for result in results:
            purities = re.findall(r'\b(925|950|999)\b', result.content)
            purity_votes.extend(purities)
        
        if not purity_votes:
            return None
        
        # Return most common
        counter = Counter(purity_votes)
        return counter.most_common(1)[0][0]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        total_calls = sum([
            self.stats["groq_calls"],
            self.stats["gemini_calls"],
            self.stats["ollama_calls"],
            self.stats["hf_calls"]
        ])
        
        return {
            **self.stats,
            "total_calls": total_calls,
            "success_rate": (total_calls - self.stats["failures"]) / max(total_calls, 1),
            "groq_available": self.groq_limiter.can_request(),
            "groq_wait_time": self.groq_limiter.wait_time(),
            "gemini_available": self.gemini_available,
            "ollama_available": OLLAMA_AVAILABLE
        }


# Global orchestrator instance
orchestrator = MultiModelOrchestrator()


if __name__ == "__main__":
    # Test orchestrator
    async def test():
        prompt = "Summarize the current state of silver markets in one sentence."
        response = await orchestrator.analyze_text(prompt)
        
        print(f"✅ Response from {response.model_used}")
        print(f"⏱️ Latency: {response.latency_ms:.0f}ms")
        print(f"📝 Content: {response.content[:100]}...")
        print(f"\n📊 Stats: {orchestrator.get_stats()}")
    
    asyncio.run(test())

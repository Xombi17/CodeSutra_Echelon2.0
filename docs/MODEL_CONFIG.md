# Model Configuration Guide

## 📊 Current Setup: Hybrid Strategy

**TEXT Generation (Narrative Analysis, Decision Making):**
```
1. Groq (Primary) - Fast cloud inference
2. Google Gemini (Fallback) - Free tier
3. Ollama (Optional) - Your local models (GPT4All, Llama, etc.)
```

**VISION Tasks (Silver Scanner - Phase 8):**
```
1. Groq Vision (Primary) - llama-3.2-90b-vision
2. Google Gemini Vision (Fallback) - gemini-2.0-flash-exp
```

✅ **No need to download large vision models in Ollama!**

---

## 🔧 Configuration

### Using Your Ollama Models

The system is configured to use `gpt4all` by default. To change:

**Edit `backend/orchestrator.py` line 359:**
```python
kwargs = {"model": "gpt4all", "messages": messages}  # Change model name
```

**Available Ollama models** (check with `ollama list`):
- `gpt4all` - GPT4All model
- `llama3.2` - Llama 3.2 small
- `gemma2` - Google Gemma 2
- ANY model you've pulled

---

## 🚀 API Keys Needed

### Option 1: Full Cloud (Recommended for Hackathon)
```bash
GROQ_API_KEY=gsk_xxx  # Required - https://console.groq.com
```

**Text**: Groq only (fast, unlimited free tier)  
**Vision**: Groq only (fast)

### Option 2: Hybrid (Your Setup)
```bash
GROQ_API_KEY=gsk_xxx         # Primary
GEMINI_API_KEY=xxx           # Fallback for vision
# Ollama runs locally (no key needed)
```

**Text**: Groq → Ollama (your GPT4All)  
**Vision**: Groq → Google Gemini

### Option 3: Maximum Reliability
```bash
GROQ_API_KEY=gsk_xxx         # Primary  
GEMINI_API_KEY=xxx           # Fallback
# Ollama runs locally
```

**Text**: Groq → Google Gemini → Ollama  
**Vision**: Groq → Google Gemini

---

## 📦 Installation

### Minimal (Cloud Only)
```bash
pip install groq google-generativeai
```

### Hybrid (Your Setup)
```bash
pip install groq google-generativeai ollama

# Ollama should already be installed
# Just make sure service is running:
ollama serve &
```

---

## 🧪 Testing Model Fallback

```bash
cd backend
python orchestrator.py
```

This will test all available models and show you the fallback chain.

---

## ⚡ Performance

| Model | Speed | Cost | Reliability |
|-------|-------|------|-------------|
| Groq | 500-800 tok/s | Free | Rate limited (30 req/min) |
| Gemini | 100-200 tok/s | Free | Unlimited |
| Ollama | 20-50 tok/s | Free | 100% (local) |

**Strategy**: Groq for speed, fallback ensures 99.9% uptime

---

## 🎯 For This Hackathon

**Recommended**: Just use **Groq + your existing Ollama** (no Gemini needed)
- Get Groq key: https://console.groq.com (instant, free)
- Your Ollama already has text models
- Vision will work via Groq (no local models needed)

**Backup plan** if hit rate limits: Add Gemini key for extra reliability

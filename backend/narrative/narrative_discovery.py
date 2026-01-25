"""
Narrative Discovery Engine
Processes 90+ articles → Top 5 validated narratives

Pipeline:
1. Content Validation (filter fake/irrelevant)
2. Relevance Scoring (silver-specific)
3. Theme Extraction (AI-powered)
4. Clustering (group similar narratives)
5. Credibility Scoring (source quality)
6. Ranking (top 5 selection)
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import re

# ML/NLP imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hdbscan
import numpy as np
from sentence_transformers import SentenceTransformer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# LLM import
from groq import Groq
from config import config


@dataclass
class Article:
    """Structured article data"""
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    author: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Narrative:
    """Discovered narrative with metadata"""
    theme: str
    description: str
    articles: List[Article]
    strength: float  # 0-100
    credibility: float  # 0-100
    sentiment: float  # -1 to 1
    velocity: float  # trending speed
    article_count: int
    sources: List[str]
    keywords: List[str]
    first_seen: datetime
    last_seen: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert narrative to JSON-serializable dict"""
        return {
            "theme": self.theme,
            "description": self.description,
            "strength": round(self.strength, 2),
            "credibility": round(self.credibility, 2),
            "sentiment": round(self.sentiment, 3),
            "velocity": round(self.velocity, 2),
            "article_count": self.article_count,
            "sources": self.sources,
            "keywords": self.keywords,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "sample_articles": [
                {
                    "title": a.title,
                    "url": a.url,
                    "source": a.source,
                    "published_at": a.published_at.isoformat()
                }
                for a in self.articles[:3]  # Top 3 articles
            ]
        }


class NarrativeDiscoveryEngine:
    """
    Discovers and validates narratives from collected articles
    """
    
    def __init__(self):
        self.groq = Groq(api_key=config.model.groq_api_key)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Load sentence transformer for semantic similarity
        print("📥 Loading sentence transformer model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, good quality
        
        # Source credibility weights
        self.source_credibility = {
            # Tier 1: Highly credible (0.9-1.0)
            "reuters": 1.0,
            "bloomberg": 0.95,
            "wsj": 0.95,
            "ft": 0.95,
            "marketwatch": 0.9,
            
            # Tier 2: Credible (0.7-0.89)
            "cnbc": 0.85,
            "forbes": 0.85,
            "kitco": 0.85,  # Silver-specific authority
            "investing.com": 0.8,
            "yahoo": 0.75,
            
            # Tier 3: Moderate (0.5-0.69)
            "reddit": 0.6,
            "twitter": 0.5,
            "seekingalpha": 0.65,
            
            # Tier 4: Low credibility (0.3-0.49)
            "telegram": 0.4,
            "stocktwits": 0.4,
            
            # Default
            "unknown": 0.5
        }
        
        # Silver-specific keywords for relevance
        self.silver_keywords = {
            # Core terms (high weight)
            "silver": 3.0,
            "xag": 2.5,
            "slv": 2.5,
            "pslv": 2.0,
            
            # Market terms (medium weight)
            "precious metals": 2.0,
            "commodity": 1.5,
            "futures": 1.5,
            "spot price": 2.0,
            
            # Industry terms (medium weight)
            "solar panels": 1.8,
            "electric vehicles": 1.8,
            "industrial demand": 2.0,
            "supply shortage": 2.5,
            "mining": 1.5,
            
            # Trading terms (low-medium weight)
            "etf": 1.5,
            "bullion": 2.0,
            "physical silver": 2.0,
            
            # Related assets (low weight)
            "gold": 0.8,
            "copper": 0.7,
            "platinum": 0.7
        }
    
    async def discover_narratives(
        self,
        articles: List[Dict[str, Any]],
        top_n: int = 5
    ) -> Tuple[List[Narrative], Dict[str, Any]]:
        """
        Main pipeline: 90+ articles → Top 5 narratives
        
        Args:
            articles: Raw article data from collectors
            top_n: Number of top narratives to return (default 5)
            
        Returns:
            Tuple of (narratives, metadata)
        """
        import time
        start_time = time.time()
        
        print("\n" + "="*60)
        print("🔍 NARRATIVE DISCOVERY PIPELINE")
        print("="*60)
        
        metadata = {
            "total_articles_analyzed": len(articles),
            "valid_articles": 0,
            "relevant_articles": 0,
            "themes_extracted": 0,
            "clusters_formed": 0,
            "processing_time_seconds": 0
        }
        
        # Step 1: Validate & Filter
        print(f"\n📥 Input: {len(articles)} articles")
        valid_articles = await self._validate_articles(articles)
        metadata["valid_articles"] = len(valid_articles)
        print(f"✅ Step 1 - Validation: {len(valid_articles)} valid articles")
        
        if len(valid_articles) < 3:
            print("⚠️ Insufficient articles for clustering")
            metadata["processing_time_seconds"] = time.time() - start_time
            return [], metadata
        
        # Step 2: Relevance Scoring
        scored_articles = await self._score_relevance(valid_articles)
        
        # Keep top 80% by relevance
        threshold = np.percentile([a['relevance_score'] for a in scored_articles], 20)
        relevant_articles = [a for a in scored_articles if a['relevance_score'] >= threshold]
        metadata["relevant_articles"] = len(relevant_articles)
        print(f"✅ Step 2 - Relevance: {len(relevant_articles)} relevant articles (threshold: {threshold:.2f})")
        
        if len(relevant_articles) < 3:
            print("⚠️ Insufficient relevant articles")
            metadata["processing_time_seconds"] = time.time() - start_time
            return [], metadata
        
        # Step 3: AI Theme Extraction
        themes = await self._extract_themes(relevant_articles)
        metadata["themes_extracted"] = len(themes)
        print(f"✅ Step 3 - Theme Extraction: {len(themes)} themes identified")
        
        # Step 4: Semantic Clustering
        clusters = await self._cluster_articles(relevant_articles, themes)
        metadata["clusters_formed"] = len(clusters)
        print(f"✅ Step 4 - Clustering: {len(clusters)} narrative clusters formed")
        
        # Step 5: Build Narratives with Credibility
        narratives = await self._build_narratives(clusters, relevant_articles)
        print(f"✅ Step 5 - Narrative Building: {len(narratives)} narratives created")
        
        # Step 6: Rank and Select Top N
        top_narratives = await self._rank_narratives(narratives, top_n)
        print(f"✅ Step 6 - Ranking: Top {len(top_narratives)} narratives selected")
        
        metadata["processing_time_seconds"] = round(time.time() - start_time, 2)
        
        return top_narratives, metadata
    
    async def _validate_articles(self, articles: List[Dict]) -> List[Article]:
        """
        Step 1: Filter out fake, irrelevant, or low-quality articles
        """
        valid = []
        
        for article in articles:
            # Skip if missing critical fields
            if not article.get('title') or not article.get('content'):
                continue
            
            # Skip if content too short (likely not real article)
            if len(article.get('content', '')) < 100:
                continue
            
            # Skip if title is spammy
            title = article['title'].lower()
            spam_indicators = ['click here', 'buy now', 'limited offer', 'shocking']
            if any(spam in title for spam in spam_indicators):
                continue
            
            # Ensure published_at is datetime
            published_at = article.get('published_at')
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    published_at = datetime.now(timezone.utc)
            elif not isinstance(published_at, datetime):
                published_at = datetime.now(timezone.utc)
            
            # Convert to Article object
            valid.append(Article(
                title=article['title'],
                content=article['content'],
                url=article.get('url', ''),
                source=article.get('source', 'unknown'),
                published_at=published_at,
                author=article.get('author', 'unknown'),
                metadata=article.get('metadata', {})
            ))
        
        return valid
    
    async def _score_relevance(self, articles: List[Article]) -> List[Dict]:
        """
        Step 2: Score each article's relevance to silver markets
        """
        scored = []
        
        for article in articles:
            text = f"{article.title} {article.content}".lower()
            
            # Calculate keyword-based relevance
            relevance_score = 0.0
            matched_keywords = []
            
            for keyword, weight in self.silver_keywords.items():
                count = text.count(keyword.lower())
                if count > 0:
                    relevance_score += weight * min(count, 3)  # Cap at 3 mentions
                    matched_keywords.append(keyword)
            
            # Normalize to 0-100
            relevance_score = min(relevance_score * 2, 100)
            
            scored.append({
                'article': article,
                'relevance_score': relevance_score,
                'matched_keywords': matched_keywords
            })
        
        return sorted(scored, key=lambda x: x['relevance_score'], reverse=True)
    
    async def _extract_themes(self, articles: List[Dict]) -> List[str]:
        """
        Step 3: Use AI to extract main themes from articles
        """
        # Sample articles for theme extraction (max 20 for speed)
        sample_size = min(20, len(articles))
        sample = articles[:sample_size]
        
        # Prepare prompt
        titles = "\n".join([f"{i+1}. {a['article'].title}" for i, a in enumerate(sample)])
        
        prompt = f"""Analyze these {sample_size} silver market article titles and identify the main themes/narratives:

{titles}

Extract 5-8 distinct themes. For each theme, provide:
1. Theme name (2-4 words)
2. Brief description (one sentence)

Format as JSON:
[
  {{"theme": "Industrial Demand Surge", "description": "Increased silver use in solar panels and EVs"}},
  ...
]

Return ONLY the JSON array, no other text."""

        try:
            response = self.groq.chat.completions.create(
                model=config.model.text_narrative,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse JSON response
            import json
            themes_raw = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            themes_raw = themes_raw.replace('```json', '').replace('```', '').strip()
            themes_data = json.loads(themes_raw)
            
            themes = [t['theme'] for t in themes_data]
            return themes
            
        except Exception as e:
            print(f"⚠️ AI theme extraction failed: {e}")
            # Fallback: extract themes from TF-IDF
            return self._extract_themes_tfidf(articles)
    
    def _extract_themes_tfidf(self, articles: List[Dict]) -> List[str]:
        """Fallback: Extract themes using TF-IDF"""
        texts = [a['article'].title + " " + a['article'].content[:500] for a in articles]
        
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        try:
            vectorizer.fit_transform(texts)
            # Get top keywords as themes
            feature_names = vectorizer.get_feature_names_out()
            return list(feature_names[:8])  # Top 8 keywords as themes
        except:
            return ["Market Movement", "Price Analysis", "Supply Demand", "Industry News"]
    
    async def _cluster_articles(
        self,
        articles: List[Dict],
        themes: List[str]
    ) -> List[List[int]]:
        """
        Step 4: Cluster articles by semantic similarity
        """
        # Create embeddings
        texts = [f"{a['article'].title} {a['article'].content[:500]}" for a in articles]
        embeddings = self.embedder.encode(texts, show_progress_bar=False)
        
        # Cluster with HDBSCAN
        min_cluster_size = max(3, len(articles) // 10)  # Dynamic based on article count
        
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=2,
            metric='euclidean'
        )
        
        labels = clusterer.fit_predict(embeddings)
        
        # Group articles by cluster
        clusters = defaultdict(list)
        for idx, label in enumerate(labels):
            if label != -1:  # Skip noise
                clusters[label].append(idx)
        
        return list(clusters.values())
    
    async def _build_narratives(
        self,
        clusters: List[List[int]],
        articles: List[Dict]
    ) -> List[Narrative]:
        """
        Step 5: Build narrative objects from clusters
        """
        narratives = []
        
        for cluster_indices in clusters:
            if len(cluster_indices) < 2:  # Skip single-article clusters
                continue
            
            cluster_articles = [articles[i]['article'] for i in cluster_indices]
            
            # Extract theme (most common keywords)
            all_keywords = []
            for i in cluster_indices:
                all_keywords.extend(articles[i]['matched_keywords'])
            
            keyword_counts = defaultdict(int)
            for kw in all_keywords:
                keyword_counts[kw] += 1
            
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            theme = " + ".join([kw[0].title() for kw in top_keywords[:2]])
            
            # Calculate metrics
            avg_relevance = np.mean([articles[i]['relevance_score'] for i in cluster_indices])
            
            # Sentiment analysis
            sentiments = []
            for article in cluster_articles:
                score = self.sentiment_analyzer.polarity_scores(article.content)
                sentiments.append(score['compound'])
            avg_sentiment = np.mean(sentiments)
            
            # Source credibility
            sources = [a.source for a in cluster_articles]
            credibility_scores = [self._get_source_credibility(s) for s in sources]
            avg_credibility = np.mean(credibility_scores) * 100
            
            # Velocity (recency weight)
            time_diffs = [(datetime.now(timezone.utc) - a.published_at).total_seconds() / 3600 
                         for a in cluster_articles]
            velocity = 100 / (1 + np.mean(time_diffs) / 24)  # Decay over days
            
            # Narrative strength (weighted combination)
            strength = (
                avg_relevance * 0.4 +
                avg_credibility * 0.3 +
                velocity * 0.2 +
                (len(cluster_articles) / len(articles) * 100) * 0.1
            )
            
            narratives.append(Narrative(
                theme=theme,
                description=self._generate_description(cluster_articles),
                articles=cluster_articles,
                strength=strength,
                credibility=avg_credibility,
                sentiment=avg_sentiment,
                velocity=velocity,
                article_count=len(cluster_articles),
                sources=list(set(sources)),
                keywords=[kw[0] for kw in top_keywords],
                first_seen=min(a.published_at for a in cluster_articles),
                last_seen=max(a.published_at for a in cluster_articles)
            ))
        
        return narratives
    
    def _get_source_credibility(self, source: str) -> float:
        """Get credibility score for a source"""
        source_lower = source.lower()
        
        for key, score in self.source_credibility.items():
            if key in source_lower:
                return score
        
        return self.source_credibility['unknown']
    
    def _generate_description(self, articles: List[Article]) -> str:
        """Generate narrative description from articles"""
        # Use first article's title/content as base
        if articles:
            title = articles[0].title
            # Extract first sentence from content
            content = articles[0].content
            first_sentence = content.split('.')[0] if '.' in content else content[:150]
            return f"{title}. {first_sentence}."[:200]
        return "No description available"
    
    async def _rank_narratives(
        self,
        narratives: List[Narrative],
        top_n: int
    ) -> List[Narrative]:
        """
        Step 6: Rank narratives and select top N
        """
        # Sort by strength (already calculated)
        ranked = sorted(narratives, key=lambda n: n.strength, reverse=True)
        
        return ranked[:top_n]


# Convenience function for API usage
async def discover_narratives_from_data(
    data: Dict[str, Any],
    top_n: int = 5
) -> Dict[str, Any]:
    """
    Discover narratives from collected data
    
    Args:
        data: Data dict from DataCollectionOrchestrator.collect_all()
        top_n: Number of top narratives to return
        
    Returns:
        Dict with narratives and metadata
    """
    engine = NarrativeDiscoveryEngine()
    narratives, metadata = await engine.discover_narratives(data['articles'], top_n)
    
    return {
        "narratives": [n.to_dict() for n in narratives],
        "metadata": metadata
    }


async def test():
    """Test the narrative discovery engine"""
    from data_collection import collector
    
    print("🚀 Testing Narrative Discovery Engine")
    print("="*60)
    
    # Collect data
    print("\n📥 Collecting data...")
    data = await collector.collect_all(news_days_back=7)
    articles = data['articles']
    
    print(f"Collected {len(articles)} total articles")
    
    # Run discovery
    engine = NarrativeDiscoveryEngine()
    narratives, metadata = await engine.discover_narratives(articles, top_n=5)
    
    # Display results
    print("\n" + "="*60)
    print("🎯 TOP 5 DISCOVERED NARRATIVES")
    print("="*60)
    
    for i, narrative in enumerate(narratives, 1):
        print(f"\n{i}. {narrative.theme}")
        print(f"   Strength: {narrative.strength:.1f}/100")
        print(f"   Credibility: {narrative.credibility:.1f}/100")
        print(f"   Sentiment: {narrative.sentiment:+.2f}")
        print(f"   Articles: {narrative.article_count}")
        print(f"   Sources: {', '.join(narrative.sources[:3])}")
        print(f"   Keywords: {', '.join(narrative.keywords[:5])}")
        print(f"   Description: {narrative.description[:150]}...")
    
    print(f"\n📊 Metadata:")
    print(f"   Total articles: {metadata['total_articles_analyzed']}")
    print(f"   Valid articles: {metadata['valid_articles']}")
    print(f"   Relevant articles: {metadata['relevant_articles']}")
    print(f"   Themes extracted: {metadata['themes_extracted']}")
    print(f"   Clusters formed: {metadata['clusters_formed']}")
    print(f"   Processing time: {metadata['processing_time_seconds']}s")


if __name__ == "__main__":
    asyncio.run(test())

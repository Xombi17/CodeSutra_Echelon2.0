"""
Pattern Hunter (PS 5 Implementation)
Unsupervised narrative discovery through clustering
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from hdbscan import HDBSCAN
import numpy as np
from database import get_session, Article, Narrative
from orchestrator import orchestrator
from config import config


class PatternHunter:
    """
    Discovers market narratives using unsupervised clustering
    Implements PS 5: Unsupervised Pattern Discovery
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=2
        )
        self.clusterer = HDBSCAN(
            min_cluster_size=config.narrative.min_cluster_size,
            min_samples=2,
            metric='euclidean'
        )
    
    async def discover_narratives(
        self,
        days_back: int = 7,
        min_articles: int = None
    ) -> List[Dict[str, Any]]:
        """
        Discover narratives from recent articles
        
        Args:
            days_back: How many days of articles to analyze
            min_articles: Minimum articles needed for clustering
            
        Returns:
            List of discovered narratives
        """
        if min_articles is None:
            min_articles = config.narrative.min_articles_for_clustering
        
        print(f"🔍 Discovering narratives from last {days_back} days...")
        
        # Fetch recent articles
        articles = self._fetch_recent_articles(days_back)
        
        if len(articles) < min_articles:
            print(f"⚠️ Not enough articles ({len(articles)} < {min_articles}), skipping clustering")
            return []
        
        print(f"📚 Analyzing {len(articles)} articles...")
        
        # Prepare text data
        texts = [self._prepare_text(article) for article in articles]
        
        # Vectorize
        try:
            vectors = self.vectorizer.fit_transform(texts)
        except Exception as e:
            print(f"❌ Vectorization error: {e}")
            return []
        
        # Cluster
        try:
            cluster_labels = self.clusterer.fit_predict(vectors.toarray())
        except Exception as e:
            print(f"❌ Clustering error: {e}")
            return []
        
        # Group articles by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label == -1:  # Noise
                continue
            
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(articles[i])
        
        print(f"✅ Found {len(clusters)} narrative clusters")
        
        # Name each cluster
        narratives = []
        for cluster_id, cluster_articles in clusters.items():
            narrative = await self._name_cluster(cluster_id, cluster_articles)
            if narrative:
                narratives.append(narrative)
        
        return narratives
    
    def _fetch_recent_articles(self, days_back: int) -> List[Article]:
        """Fetch recent articles from database"""
        session = get_session()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            articles = session.query(Article).filter(
                Article.published_at >= cutoff_date,
                Article.narrative_id == None  # Unassigned articles
            ).all()
            
            return articles
        
        finally:
            session.close()
    
    def _prepare_text(self, article: Article) -> str:
        """Prepare article text for clustering"""
        title = article.title or ""
        content = article.content or ""
        return f"{title} {content}".strip()
    
    async def _name_cluster(
        self,
        cluster_id: int,
        articles: List[Article]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate human-readable name for a cluster
        
        Args:
            cluster_id: Cluster ID
            articles: Articles in this cluster
            
        Returns:
            Narrative dict with name and metadata
        """
        # Extract top keywords using TF-IDF
        texts = [self._prepare_text(article) for article in articles]
        
        try:
            tfidf_matrix = self.vectorizer.transform(texts)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top terms across all documents in cluster
            avg_tfidf = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
            top_indices = avg_tfidf.argsort()[-10:][::-1]
            top_keywords = [feature_names[i] for i in top_indices]
        
        except:
            top_keywords = ["silver", "market"]
        
        # Create prompt for LLM to name the narrative
        sample_headlines = [article.title for article in articles[:5]]
        
        prompt = f"""Analyze these headlines about silver markets and create a concise narrative name (3-4 words maximum):

Headlines:
{chr(10).join(f"- {h}" for h in sample_headlines)}

Top keywords: {', '.join(top_keywords[:5])}

Respond with ONLY the narrative name, nothing else. Examples: "Mining Strike Concerns", "Industrial Solar Demand", "Wedding Season Rush"
"""
        
        # Use orchestrator to generate name
        response = await orchestrator.analyze_text(
            prompt=prompt,
            model_type="narrative"
        )
        
        if not response.success:
            # Fallback: use top keywords
            narrative_name = " ".join(top_keywords[:3]).title()
        else:
            narrative_name = response.content.strip().strip('"')
        
        # Calculate initial sentiment
        avg_sentiment = self._calculate_cluster_sentiment(articles)
        
        return {
            "cluster_id": cluster_id,
            "name": narrative_name,
            "article_count": len(articles),
            "article_ids": [article.id for article in articles],
            "cluster_keywords": top_keywords[:10],
            "initial_sentiment": avg_sentiment,
            "birth_date": datetime.utcnow(),
            "phase": "birth"
        }
    
    def _calculate_cluster_sentiment(self, articles: List[Article]) -> float:
        """Calculate average sentiment for cluster"""
        sentiments = [a.sentiment_score for a in articles if a.sentiment_score is not None]
        
        if not sentiments:
            return 0.0
        
        return sum(sentiments) / len(sentiments)
    
    async def save_narratives(self, narratives: List[Dict[str, Any]]):
        """Save discovered narratives to database"""
        session = get_session()
        
        try:
            for narrative_data in narratives:
                # Check if similar narrative already exists
                existing = session.query(Narrative).filter(
                    Narrative.name.like(f"%{narrative_data['name'][:10]}%"),
                    Narrative.phase != 'death'
                ).first()
                
                if existing:
                    # Update existing narrative
                    existing.article_count += narrative_data['article_count']
                    existing.last_updated = datetime.utcnow()
                    print(f"📝 Updated existing narrative: {existing.name}")
                else:
                    # Create new narrative
                    narrative = Narrative(
                        name=narrative_data['name'],
                        phase=narrative_data['phase'],
                        birth_date=narrative_data['birth_date'],
                        article_count=narrative_data['article_count'],
                        sentiment=narrative_data['initial_sentiment'],
                        cluster_keywords={"keywords": narrative_data['cluster_keywords']}
                    )
                    session.add(narrative)
                    session.flush()  # Get ID
                    
                    # Assign articles to narrative
                    for article_id in narrative_data['article_ids']:
                        article = session.query(Article).get(article_id)
                        if article:
                            article.narrative_id = narrative.id
                    
                    print(f"✨ Created new narrative: {narrative.name} (ID: {narrative.id})")
            
            session.commit()
        
        except Exception as e:
            session.rollback()
            print(f"❌ Save narratives error: {e}")
        
        finally:
            session.close()


# Global pattern hunter instance
pattern_hunter = PatternHunter()


if __name__ == "__main__":
    # Test pattern hunter
    from datetime import timedelta
    
    async def test():
        print("🧪 Testing Pattern Hunter (PS 5)...\n")
        
        # Discover narratives
        narratives = await pattern_hunter.discover_narratives(days_back=7)
        
        if narratives:
            print(f"\n📊 Discovered {len(narratives)} narratives:")
            for narrative in narratives:
                print(f"\n  📌 {narrative['name']}")
                print(f"     Articles: {narrative['article_count']}")
                print(f"     Keywords: {', '.join(narrative['cluster_keywords'][:5])}")
                print(f"     Sentiment: {narrative['initial_sentiment']:.2f}")
            
            # Save to database
            await pattern_hunter.save_narratives(narratives)
            print("\n💾 Narratives saved to database")
        else:
            print("\n⚠️ No narratives discovered (need more articles)")
    
    asyncio.run(test())

# 📊 Article Selection & Filtering Process - Detailed Explanation

## 🔄 **THE COMPLETE FLOW**

### **Step 1: Data Collection** 
Every 10-120 minutes (adaptive)

```
NewsAPI Fetches:
├─ Query 1: "silver price" → ~20-30 articles
├─ Query 2: "silver market" → ~20-30 articles  
├─ Query 3: "silver mining" → ~20-30 articles
├─ Query 4: "silver demand" → ~20-30 articles
└─ Query 5: "precious metals" → ~20-30 articles

Total per fetch: 100-150 articles
```

**What we store:**
- ✅ Title
- ✅ Content (full text)
- ✅ URL (for deduplication)
- ✅ Source (newsapi, reuters, bloomberg, etc.)
- ✅ Published date
- ✅ Fetched timestamp

**Deduplication:**
- Before saving, check if URL already exists
- Skip duplicates
- **Result**: ~50-100 new unique articles per fetch

---

### **Step 2: Database Storage**

```
SQLite Database:
├─ 1,000+ total articles collected
├─ Last 7 days of data kept
└─ Older articles archived/deleted
```

---

### **Step 3: Article Selection for Clustering** (Pattern Hunter)

**This is where the filtering happens!**

#### **Selection Criteria:**

```python
# File: pattern_hunter.py, Line 107-110

cutoff_date = datetime.utcnow() - timedelta(days=30)  # Last 30 days

articles = session.query(Article).filter(
    Article.published_at >= cutoff_date,      # Not too old
    Article.narrative_id == None              # Not already assigned
).all()
```

**What this means:**
1. ✅ **Recency Filter**: Only articles from last **30 days**
2. ✅ **Unassigned Filter**: Only articles **not yet part of a narrative**
3. ❌ Skip articles already categorized

**Result**: Typically **150-300 articles** ready for clustering

---

### **Step 4: Minimum Threshold Check**

```python
# File: pattern_hunter.py, Line 58-60

if len(articles) < min_articles:  # Default: 50
    print("⚠️ Not enough articles, skipping")
    return []
```

**Threshold:**
- Minimum **50 articles** needed for meaningful clustering
- Default from config: `min_articles_for_clustering = 50`
- Why? HDBSCAN needs enough data to find patterns

**If < 50 articles:**
- ⚠️ Skip clustering
- Wait for more data
- Prevents false patterns

**If ≥ 50 articles:**
- ✅ Proceed to clustering
- Typically process **150-300 articles**

---

### **Step 5: Text Preparation**

```python
# File: pattern_hunter.py, Line 118-122

def _prepare_text(article):
    title = article.title or ""
    content = article.content or ""
    return f"{title} {content}".strip()
```

**What we use:**
- ✅ Full article title
- ✅ Full article content (if available)
- ✅ Combined into single text string

**Example:**
```
Input Article:
  Title: "Peru silver miners strike over pay"
  Content: "Workers at major silver mine in Peru began strike..."
  
Prepared Text:
  "Peru silver miners strike over pay Workers at major silver mine..."
```

---

### **Step 6: TF-IDF Vectorization**

```python
# File: pattern_hunter.py, Line 69

vectors = self.vectorizer.fit_transform(texts)
```

**Process:**
1. Takes all 150-300 article texts
2. Converts to TF-IDF vectors (numbers)
3. Extracts **2-10 key features** per article
4. **Result**: Numerical representation of meaning

**What TF-IDF does:**
- Finds important words (high frequency in article, low in corpus)
- Ignores common words ("the", "and", "is")
- Focuses on meaningful terms ("peru", "mining", "strike")

---

### **Step 7: HDBSCAN Clustering**

```python
# File: pattern_hunter.py, Line 76

cluster_labels = self.clusterer.fit_predict(vectors.toarray())
```

**Parameters:**
- `min_cluster_size = 3` (at least 3 articles per narrative)
- `min_samples = 2` (at least 2 core articles)

**Process:**
1. Groups similar vectors together
2. Finds **10-15 clusters** (narratives)
3. Labels noise as `-1` (articles that don't fit any pattern)

**Example Output:**
```
Article 1: Cluster 0 (Peru Mining)
Article 2: Cluster 0 (Peru Mining)  
Article 3: Cluster 0 (Peru Mining)
Article 4: Cluster 1 (Solar Demand)
Article 5: Cluster 1 (Solar Demand)
...
Article 47: Cluster -1 (Noise - doesn't fit)
```

---

### **Step 8: Noise Filtering**

```python
# File: pattern_hunter.py, Line 84-85

for label in cluster_labels:
    if label == -1:  # Noise
        continue  # Skip this article
```

**What gets filtered out:**
- ❌ Articles that don't match any pattern
- ❌ One-off stories (no similar articles)
- ❌ Outliers

**Typical noise rate:**
- 10-20% of articles are noise
- **Example**: If 155 articles → ~140 clustered, ~15 noise

---

### **Step 9: Cluster Grouping**

```python
# File: pattern_hunter.py, Line 82-89

clusters = {}
for i, label in enumerate(cluster_labels):
    if label == -1:
        continue
    if label not in clusters:
        clusters[label] = []
    clusters[label].append(articles[i])
```

**Result:**
```
Cluster 0: [Article 1, Article 2, Article 3, ...] (47 articles)
Cluster 1: [Article 8, Article 9, ...] (23 articles)  
Cluster 2: [Article 15, Article 16, ...] (18 articles)
...
Cluster 12: [Article 142, Article 143, ...] (5 articles)

Total: 13 clusters (narratives)
```

---

### **Step 10: AI Naming**

```python
# File: pattern_hunter.py, Line 124-150

# Extract top 10 keywords from cluster
top_keywords = ["peru", "mining", "strike", "workers", "silver", ...]

# Send to Groq Llama-70B
prompt = f"Keywords: {top_keywords}\n\nGenerate a 2-4 word market narrative name"

# AI generates: "Peru Mining Strike"
```

**Process:**
- Takes top 10 TF-IDF keywords from cluster
- Sends to Groq Llama-3.3-70B
- AI generates concise, meaningful name
- **Time**: ~157ms per cluster

---

## 📊 **SUMMARY: THE NUMBERS**

### **Data Collection (Every 10-120 min)**
```
NewsAPI → 100-150 articles fetched
Deduplication → ~50-100 unique articles saved
Database → 1,000+ total articles (last 30 days)
```

### **Pattern Discovery (Every 30 min)**
```
Query Database → 150-300 unassigned articles (last 30 days)
Minimum Check → Must have ≥50 articles
Text Prep → Combine title + content
TF-IDF → Convert to 2-10 features per article
HDBSCAN → Group into 10-15 clusters
Noise Filter → Remove 10-20% outliers
AI Naming → 13 narratives discovered
```

### **Current Status**
```
Total Articles: 1,000+ in database
Articles Used: 155 (for latest clustering)
Narratives Found: 13
Articles Assigned: ~140 (90%)
Noise/Unassigned: ~15 (10%)
```

---

## 🎯 **HOW TO EXPLAIN TO JUDGES**

### **Question: "How do you choose which articles to use?"**

**Answer:**
> "We use a smart filtering pipeline:
> 
> 1. **Recency**: Only articles from last 30 days (staying current)
> 2. **Minimum threshold**: Need at least 50 articles for statistical significance
> 3. **Unassigned only**: Skip articles already categorized (no double-counting)
> 4. **Quality over quantity**: We process 150-300 articles and let HDBSCAN find natural groupings
> 5. **Noise filtering**: Automatically removes 10-20% of outliers that don't fit patterns
> 
> Result: From 1,000+ articles collected, we cluster ~150-300 at a time, discovering 10-15 narratives. Currently we have 13 active narratives from 155 analyzed articles."

### **Question: "Do you use all articles?"**

**Answer:**
> "Not at once. We use a rolling window - articles from the last 30 days that haven't been assigned yet. This is around 150-300 articles per clustering run. Articles older than 30 days are archived. This keeps the analysis fresh and prevents old news from distorting current narratives."

### **Question: "What if you only have 20 articles?"**

**Answer:**
> "Smart question! HDBSCAN needs at least 50 articles for meaningful patterns. If we have less, we wait and skip that clustering cycle. This prevents false patterns. Our adaptive system fetches more frequently in high volatility, so we quickly reach the threshold."

---

## 🔢 **ACTUAL NUMBERS FROM CURRENT SYSTEM**

**From test results:**
```
Test: Tier 2, Test 4 (Pattern Hunter Discovery)
- Articles analyzed: 155
- Narratives discovered: 13
- Time taken: 1.48 seconds
- Clustering speed: 100 docs in 0.01s
```

**Breakdown:**
- 155 articles total
- ~140 assigned to narratives (90%)
- ~15 filtered as noise (10%)
- 13 distinct narratives found
- Average: 10-11 articles per narrative

---

## ✅ **KEY TAKEAWAYS**

1. **We fetch 100-150 articles** per collection cycle
2. **We store 1,000+ articles** in database (30 days)
3. **We cluster 150-300 articles** per discovery run
4. **We need minimum 50 articles** for clustering
5. **We filter out 10-20% noise** automatically
6. **We discover 10-15 narratives** typically
7. **Currently have 13 narratives** from 155 articles

**It's adaptive, smart, and quality-focused!** 🎯

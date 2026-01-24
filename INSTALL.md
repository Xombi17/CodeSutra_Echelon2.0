# 🚀 Quick Installation Guide

## The Error You're Seeing

Python 3.14 is too new and has permission issues with pip. Let's install manually.

---

## ✅ Manual Installation (5 minutes)

### Step 1: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies (Skip Scanner)
```bash
cd backend
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

**If you still get errors**, install only the core packages:
```bash
pip install fastapi uvicorn python-dotenv pydantic pydantic-settings
pip install groq google-generativeai ollama
pip install scikit-learn hdbscan vaderSentiment
pip install yfinance praw requests beautifulsoup4
pip install sqlalchemy aiosqlite redis
pip install python-socketio websockets
pip install numpy pandas python-dateutil pytz
pip install pytest httpx
```

### Step 3: Initialize Database
```bash
python database.py
```

### Step 4: Seed Demo Data
```bash
python seed_demo_data.py
```

### Step 5: Add API Key
```bash
cd ..
nano .env  # Or use any editor
# Add line: GROQ_API_KEY=gsk_your_key_here
```

### Step 6: Start Backend
```bash
cd backend
uvicorn main:app --reload
```

---

## 🎯 Even Simpler (If Issues Persist)

Use **Python 3.11 or 3.12** instead of 3.14:

```bash
# Check if you have Python 3.12
python3.12 --version

# If yes, use it
python3.12 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

---

## ✅ Verification

Once running, visit:
- http://localhost:8000 (should show {"status": "online"})
- http://localhost:8000/docs (API documentation)

---

**Need help?** The backend code is ready. Installation issues are just Python 3.14 compatibility. Use 3.11-3.13 for smoother install.

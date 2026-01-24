"""
SilverSentinel Testing Dashboard
Streamlit app for testing API endpoints and camera scanning
"""
import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Helper function for safe type conversion
def safe_int(value, default=0):
    """Safely convert value to int"""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default

# Configuration
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="SilverSentinel Dashboard",
    page_icon="🥈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #C0C0C0;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #C0C0C0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .narrative-birth { color: #90EE90; }
    .narrative-growth { color: #32CD32; }
    .narrative-peak { color: #FFD700; }
    .narrative-reversal { color: #FF6347; }
    .narrative-death { color: #808080; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🥈 SilverSentinel Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🥈 Silver Sentinel")
    st.markdown("### Navigation")
    
    # API Health Check
    try:
        health = requests.get(f"{API_BASE}/", timeout=2)
        if health.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Offline")
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh All Data"):
        st.cache_data.clear()
        st.rerun()

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "📰 Narratives", 
    "📈 Trading Agent",
    "📷 Silver Scanner",
    "🛠️ API Tester"
])

# ==================== TAB 1: Dashboard ====================
with tab1:
    st.header("Market Intelligence Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch data
    try:
        narratives_resp = requests.get(f"{API_BASE}/api/narratives").json()
        narratives = narratives_resp.get("narratives", []) if isinstance(narratives_resp, dict) else narratives_resp
        
        signal_resp = requests.get(f"{API_BASE}/api/trading-signal").json()
        signal = signal_resp.get("signal", signal_resp) if isinstance(signal_resp, dict) else signal_resp
        
        stability_resp = requests.get(f"{API_BASE}/api/stability").json()
        stability = stability_resp.get("stability", stability_resp) if isinstance(stability_resp, dict) else stability_resp
        
        stats = requests.get(f"{API_BASE}/api/stats").json()
        
        with col1:
            st.metric("Active Narratives", len(narratives))
        with col2:
            action = signal.get("action", "N/A") if isinstance(signal, dict) else "N/A"
            action_color = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "🟡"
            st.metric("Trading Signal", f"{action_color} {action}")
        with col3:
            conf = signal.get("confidence", 0) if isinstance(signal, dict) else 0
            st.metric("Confidence", f"{conf*100:.1f}%")
        with col4:
            stab_label = stability.get("stability_label", "N/A") if isinstance(stability, dict) else "N/A"
            st.metric("System Stability", stab_label)
        
        st.markdown("---")
        
        # Narrative Overview
        st.subheader("📰 Active Narratives")
        if narratives:
            # Sanitize data for pandas
            clean_narratives = []
            for n in narratives:
                clean_narratives.append({
                    "Narrative": n.get("name", ""),
                    "Phase": n.get("phase", ""),
                    "Strength": safe_int(n.get("strength")),
                    "Sentiment": safe_float(n.get("sentiment")),
                    "Articles": safe_int(n.get("article_count"))
                })
            df = pd.DataFrame(clean_narratives)
            st.dataframe(df, width="stretch", hide_index=True)
        
        # Signal Details
        st.subheader("📈 Current Trading Signal")
        col1, col2 = st.columns(2)
        with col1:
            st.json(signal)
        with col2:
            st.markdown(f"**Reasoning:** {signal.get('reasoning', 'N/A')}")
            if signal.get("conflicts"):
                conflicts = signal["conflicts"]
                if isinstance(conflicts, list) and len(conflicts) > 0:
                    # Handle if conflict is a dict (new format) or string
                    conflict_names = []
                    for c in conflicts:
                        if isinstance(c, dict):
                            conflict_names.append(c.get("narrative_name", "Unknown"))
                        else:
                            conflict_names.append(str(c))
                    st.warning(f"⚠️ Conflicts: {', '.join(conflict_names)}")
                else:
                    st.warning(f"⚠️ Conflicts detected")
                
    except Exception as e:
        st.error(f"Error fetching data: {e}")

# ==================== TAB 2: Narratives ====================
with tab2:
    st.header("📰 Narrative Intelligence")
    
    try:
        narratives_resp = requests.get(f"{API_BASE}/api/narratives").json()
        narratives = narratives_resp.get("narratives", []) if isinstance(narratives_resp, dict) else narratives_resp
        
        if narratives:
            for n in narratives:
                phase_emoji = {
                    "birth": "🌱", "growth": "📈", "peak": "⛰️", 
                    "reversal": "📉", "death": "💀"
                }.get(n["phase"], "❓")
                
                with st.expander(f"{phase_emoji} {n['name']} - {n['phase'].upper()}", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Strength", f"{safe_int(n.get('strength'))}/100")
                    col2.metric("Sentiment", f"{safe_float(n.get('sentiment')):.2f}")
                    col3.metric("Articles", safe_int(n.get("article_count")))
                    # Safe type conversion for age_days
                    age = safe_int(n.get('age_days'))
                    col4.metric("Age", f"{age} days")
                    
                    if n.get("cluster_keywords"):
                        keywords = n["cluster_keywords"]
                        # Handle if keywords is a dict (API returns {keywords: [...]})
                        if isinstance(keywords, dict):
                            keywords = keywords.get("keywords", [])
                        
                        if isinstance(keywords, list):
                            st.markdown(f"**Keywords:** {', '.join(keywords[:5])}")
                    
                    # Forecast Section
                    st.markdown("---")
                    st.markdown("🔮 **AI Forecast (48h)**")
                    try:
                        forecast_resp = requests.get(f"{API_BASE}/api/narratives/{n['id']}/forecast").json()
                        lf = forecast_resp.get("lifecycle_forecast", {})
                        pi = forecast_resp.get("price_impact_forecast", {})
                        
                        fc1, fc2 = st.columns(2)
                        with fc1:
                            st.caption("Next Likely Phase")
                            next_phase = lf.get("next_phase", "Unknown")
                            prob = safe_float(lf.get("probability")) * 100
                            st.markdown(f"**{next_phase.upper()}** ({prob:.0f}%)")
                            st.caption(f"Reason: {lf.get('reasoning', 'N/A')}")
                            
                        with fc2:
                            st.caption("Projected Price Impact")
                            direction = pi.get("direction", "neutral")
                            arrow = "↗️" if direction == "up" else "↘️" if direction == "down" else "➡️"
                            magnitude = safe_float(pi.get("magnitude_percentage"))
                            conf = safe_float(pi.get("confidence")) * 100
                            st.markdown(f"**{arrow} {magnitude:.2f}%**")
                            st.caption(f"Confidence: {conf:.0f}%")
                            
                    except Exception as e:
                        st.caption("Prediction unavailable")
        else:
            st.info("No narratives detected yet. Run the narrative discovery pipeline first.")
            
    except Exception as e:
        st.error(f"Error: {e}")

# ==================== TAB 3: Trading Agent ====================
with tab3:
    st.header("📈 Autonomous Trading Agent")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Signal")
        try:
            response = requests.get(f"{API_BASE}/api/trading-signal").json()
            signal = response.get("signal", response) if isinstance(response, dict) else response
            
            action = signal.get("action", "HOLD")
            if action == "BUY":
                st.success(f"🟢 **{action}** Signal")
            elif action == "SELL":
                st.error(f"🔴 **{action}** Signal")
            else:
                st.warning(f"🟡 **{action}** Signal")
            
            st.metric("Confidence", f"{signal.get('confidence', 0)*100:.1f}%")
            st.metric("Strength", f"{signal.get('strength', 0)}/100")
            st.metric("Position Size", f"{signal.get('position_size', 1.0)*100:.0f}%")
            
            st.markdown("**Reasoning:**")
            st.info(signal.get("reasoning", "No reasoning available"))
            
        except Exception as e:
            st.error(f"Error: {e}")
    
    with col2:
        st.subheader("Stability Analysis")
        try:
            response = requests.get(f"{API_BASE}/api/stability").json()
            stability = response.get("stability", response) if isinstance(response, dict) else response
            
            label = stability.get("risk_level", "unknown").lower()
            if label == "low":
                st.success(f"✅ Market Risk: **{label.upper()}**")
            elif label == "medium":
                st.warning(f"⚠️ Market Risk: **{label.upper()}**")
            else:
                st.error(f"🔴 Market Risk: **{label.upper()}**")
            
            st.metric("Stability Score", f"{stability.get('score', 0):.2f}")
            st.metric("Volatility", f"{stability.get('volatility', 0):.2f}%")
            st.metric("Recent Decisions", stability.get("samples", 0))
            
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    st.subheader("Signal History")
    try:
        response = requests.get(f"{API_BASE}/api/signals/history?limit=10").json()
        signals = response.get("signals", []) if isinstance(response, dict) else response
        
        if signals:
            # Sanitize data types for pandas
            clean_signals = []
            for s in signals:
                clean_signals.append({
                    "id": safe_int(s.get("id")),
                    "timestamp": s.get("timestamp", ""),
                    "action": s.get("action", ""),
                    "confidence": safe_float(s.get("confidence")),
                    "strength": safe_int(s.get("strength")),
                    "price": safe_float(s.get("price"))
                })
            df = pd.DataFrame(clean_signals)
            st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("No signal history available yet.")
    except Exception as e:
        st.error(f"Error fetching history: {e}")

# ==================== TAB 4: Silver Scanner ====================
with tab4:
    st.header("📷 Physical Silver Scanner")
    st.markdown("Capture or upload an image of silver jewelry, coins, or bars for AI-powered valuation.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["📸 Camera Capture", "📁 File Upload"],
            horizontal=True
        )
        
        image_data = None
        image_name = "capture.jpg"
        
        if input_method == "📸 Camera Capture":
            st.info("Click the checkbox below to activate camera")
            run_camera = st.checkbox("Enable Camera", key="run_camera")
            
            if run_camera:
                st.markdown("**Point your camera at the silver item and capture:**")
                camera_image = st.camera_input("Take a photo")
                if camera_image is not None:
                    image_data = camera_image.getvalue()
                    image_name = "camera_capture.jpg"
                    st.success("✅ Image captured!")
        else:
            uploaded_file = st.file_uploader(
                "Upload Silver Image",
                type=["jpg", "jpeg", "png", "webp"],
                help="Upload a clear photo of your silver item"
            )
            if uploaded_file is not None:
                image_data = uploaded_file.getvalue()
                image_name = uploaded_file.name
                try:
                    st.image(uploaded_file, caption="Uploaded Image", width="stretch")
                except ImportError:
                    st.info(f"📷 Image uploaded: {uploaded_file.name} ({len(image_data)/1024:.1f} KB)")
        
        user_id = st.text_input("User ID (optional)", value="demo_user")
        
        if image_data is not None:
            
            if st.button("🔍 Analyze Silver", type="primary"):
                with st.spinner("Analyzing image with AI vision models..."):
                    try:
                        files = {"image": (image_name, image_data, "image/jpeg")}
                        data = {"user_id": user_id}
                        
                        response = requests.post(
                            f"{API_BASE}/api/scan",
                            files=files,
                            data=data,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state["scan_result"] = result
                            st.success("✅ Analysis complete!")
                        else:
                            st.error(f"Error: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Scan failed: {e}")
    
    with col2:
        st.subheader("Analysis Results")
        
        if "scan_result" in st.session_state:
            result = st.session_state["scan_result"]
            
            # Display results
            st.markdown(f"**Detected Type:** {result.get('detected_type', 'Unknown')}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Purity", f"{result.get('purity') or 'N/A'}")
                # API returns estimated_weight_g, but check both
                weight = result.get('estimated_weight_g') or result.get('weight') or 0
                st.metric("Est. Weight", f"{weight} g")
            with col_b:
                # Handle nested valuation structure
                valuation = result.get("valuation", {})
                if isinstance(valuation, dict) and "value_range" in valuation:
                    val_range = valuation["value_range"]
                else:
                    val_range = result.get("valuation_range", {}) or {}
                
                min_val = val_range.get('min') or 0
                max_val = val_range.get('max') or 0
                st.metric("Min Value", f"₹{min_val:,.0f}")
                st.metric("Max Value", f"₹{max_val:,.0f}")
            
            st.metric("Confidence", f"{result.get('confidence', 0)*100:.1f}%")
            
            # Raw JSON
            with st.expander("View Raw Response"):
                st.json(result)
        else:
            st.info("Upload an image and click 'Analyze Silver' to see results here.")
    
    st.markdown("---")
    st.subheader("Recent Scans")
    try:
        response = requests.get(f"{API_BASE}/api/scans/user/{user_id}").json()
        scans = response.get("scans", []) if isinstance(response, dict) else []
        
        if scans:
            for scan in scans[:5]:
                val_range = scan.get("valuation_range") or {}
                max_val = val_range.get("max") or 0
                st.markdown(f"- **{scan.get('detected_type', 'Item')}** | Purity: {scan.get('purity') or 'N/A'} | Value: ₹{max_val:,.0f}")
        else:
            st.info("No previous scans for this user.")
    except:
        st.info("Scan history will appear here after your first scan.")

# ==================== TAB 5: API Tester ====================
with tab5:
    st.header("🛠️ API Endpoint Tester")
    
    endpoints = {
        "Health Check": {"method": "GET", "path": "/"},
        "Get Narratives": {"method": "GET", "path": "/api/narratives"},
        "Get Trading Signal": {"method": "GET", "path": "/api/trading-signal"},
        "Get Stability": {"method": "GET", "path": "/api/stability"},
        "Get Stats": {"method": "GET", "path": "/api/stats"},
        "Get Signal History": {"method": "GET", "path": "/api/signals/history?limit=5"},
        "Get Price History": {"method": "GET", "path": "/api/prices?limit=24"},
        "Get User Scans": {"method": "GET", "path": "/api/scans/user/demo_user"},
    }
    
    selected = st.selectbox("Select Endpoint", list(endpoints.keys()))
    
    endpoint = endpoints[selected]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        custom_path = st.text_input("Endpoint Path", value=endpoint["path"])
    with col2:
        method = st.selectbox("Method", ["GET", "POST"], index=0 if endpoint["method"] == "GET" else 1)
    
    if st.button("🚀 Send Request", type="primary"):
        try:
            with st.spinner("Making request..."):
                if method == "GET":
                    response = requests.get(f"{API_BASE}{custom_path}", timeout=10)
                else:
                    response = requests.post(f"{API_BASE}{custom_path}", timeout=10)
                
                st.markdown(f"**Status:** {response.status_code}")
                
                try:
                    st.json(response.json())
                except:
                    st.code(response.text)
                    
        except Exception as e:
            st.error(f"Request failed: {e}")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>SilverSentinel v1.0 | Built for NMIMS Hackathon 2026</p>",
    unsafe_allow_html=True
)

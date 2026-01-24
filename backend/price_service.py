"""
Real-time Price Service for Silver Market Intelligence.
Fetches live data via yfinance and calculates technical indicators.
"""
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False
    print("⚠️ yfinance/pandas not installed. Using mock strings.")

from datetime import datetime, timedelta
from typing import Dict, Any, List

class SilverPriceService:
    def __init__(self):
        self.ticker = "SI=F"  # Silver Futures
        self.mcx_ticker = "SILVER.NS"  # Proxy for MCX
        
        # Stateful Simulation (HFT Engine anchored to Reality)
        self.sim_state = {
            "price_inr": 92850.0, # Default backup
            "trend": 1,
            "volatility": 15.0,
            "logs": []
        }
        self._sync_with_real_market()
    
    def _sync_with_real_market(self):
        """Attempts to fetch REAL price to anchor the simulation."""
        if HAS_YFINANCE:
            try:
                # Fetch Silver Futures (USD) and USDINR
                si = yf.Ticker("SI=F").history(period="1d")
                usd = yf.Ticker("INR=X").history(period="1d")
                
                if not si.empty and not usd.empty:
                    price_usd = si['Close'].iloc[-1]
                    rate = usd['Close'].iloc[-1]
                    
                    # Convert to MCX equivalent (approx 1000 multiplier adjustment for kg vs oz/purity)
                    # MCX Silver is per kg. Spot Silver is per Time.
                    # Formula: (USD Price * USDINR) * 32.15 (oz to kg) * 1.15 (Import Duty/Premium)
                    real_inr_price = (price_usd * rate * 32.15) * 1.12 
                    
                    self.sim_state['price_inr'] = round(real_inr_price, 2)
                    print(f"✅ Market Data Synced: Silver @ ₹{self.sim_state['price_inr']}")
            except Exception as e:
                print(f"⚠️ Market Sync Failed: {e}")
        
    def get_current_market_data(self) -> Dict[str, Any]:
        """Fetch live silver price and key technicals."""
        if not HAS_YFINANCE:
            return self._get_fallback_data()

        try:
            # Fetch last 3 months for tech analysis
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            ticker = yf.Ticker(self.ticker)
            df = ticker.history(start=start_date, interval="1d")
            
            if df.empty:
                return self._get_fallback_data()

            current_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate Indicators
            rsi = self._calculate_rsi(df['Close'])
            sma_50 = df['Close'].rolling(window=50).mean().iloc[-1]
            sma_20 = df['Close'].rolling(window=20).mean().iloc[-1]
            
            # Volatility (ATR-like proxy)
            daily_range = (df['High'] - df['Low']) / df['Close']
            volatility = daily_range.rolling(window=14).mean().iloc[-1] * 100

            return {
                "price_usd": round(current_price, 2),
                "change_24h_pct": round(change_pct, 2),
                "rsi_14": round(rsi, 1),
                "trend_50d": "Bullish" if current_price > sma_50 else "Bearish",
                "volatility_index": round(volatility, 2), # % daily swing
                "support_level": round(df['Low'].tail(30).min(), 2),
                "resistance_level": round(df['High'].tail(30).max(), 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Price Service Error: {e}")
            return self._get_fallback_data()

    def get_historical_prices(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical daily OHLC for backtesting."""
        if not HAS_YFINANCE:
            return []

        try:
            start_date = (datetime.now() - timedelta(days=days+5)).strftime('%Y-%m-%d')
            df = yf.Ticker(self.ticker).history(start=start_date)
            
            history = []
            for date, row in df.iterrows():
                history.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "close": row['Close'],
                    "volume": row['Volume']
                })
            return history[-days:]
        except Exception:
            return []

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs.iloc[-1]))

    def get_live_simulation_packet(self) -> Dict[str, Any]:
        """
        Generate a HFT-style packet.
        Advances state by 1 tick.
        """
        import random
        
        # 1. Update Price (Random Walk with Momentum)
        change = (random.random() - 0.45) * self.sim_state['volatility']
        # 5% chance of trend switch
        if random.random() > 0.95: self.sim_state['trend'] *= -1
        
        self.sim_state['price_inr'] += (change + (self.sim_state['trend'] * 2))
        price = self.sim_state['price_inr']
        
        # 2. Generate Order Book
        asks = []
        bids = []
        for i in range(1, 6):
            asks.append({"price": int(price + i*15), "vol": round(random.uniform(0.5, 5.0), 2)})
            bids.append({"price": int(price - i*15), "vol": round(random.uniform(0.5, 5.0), 2)})
            
        # 3. Generate Log (Occasional)
        new_log = None
        if random.random() > 0.8:
            actions = ["SCANNING", "HEARTBEAT", "CALCULATING", "MAINTAIN"]
            new_log = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "action": random.choice(actions),
                "message": "Routine logic cycle complete. Variance nominal."
            }
            
        return {
            "price": round(price, 2),
            "change": round(change, 2),
            "timestamp": datetime.now().isoformat(),
            "order_book": {"asks": asks, "bids": bids},
            "system_log": new_log
        }

    def _get_fallback_data(self):
        """Mock data if API fails (offline mode)."""
        return {
            "price_usd": 31.50,
            "change_24h_pct": 1.2,
            "rsi_14": 55.0,
            "trend_50d": "Bullish",
            "volatility_index": 1.5,
            "support_level": 30.00,
            "resistance_level": 32.50,
            "timestamp": datetime.now().isoformat(),
            "note": "Offline/Fallback Data"
        }

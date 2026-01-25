/**
 * SilverSentinel API Client
 * Centralized API handling for the frontend
 */

// Base URL for API requests
// Fallback to '/api' (proxied via next.config.mjs) for local development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export interface TradingSignal {
    signal: {
        action: "BUY" | "SELL" | "HOLD";
        confidence: number;
        strength: number;
        reasoning: string;
        position_size: number;
        dominant_narrative: string;
        price: number;
    }
}

export interface Narrative {
    id: number | string;
    name: string;
    phase: "BIRTH" | "GROWTH" | "PEAK" | "REVERSAL" | "DEATH" | "STABLE" | "ACCUMULATION" | string;
    strength: number;
    momentum?: number;
    risk_score?: number;
    sentiment?: number;
    article_count?: number;
    last_updated?: string;
    description?: string; // Sometimes called summary
}

export interface MarketStability {
    score: number;
    status: string;
    stability: {
       score: number; // 0-100
       status: "CRITICAL" | "LOW" | "MODERATE" | "HIGH" | "OPTIMAL";
       consecutive_stable_days: number;
       risk_level: string;
    };
    alert?: string;
    timestamp: string;
}

export interface ScanResult {
    scan_id: string;
    detected_type: string;
    purity: number;
    purity_confidence: string;
    estimated_weight_g: number;
    dimensions: {
        width_mm: number;
        height_mm: number;
        thickness_mm: number;
    };
    valuation: {
        base_value: number;
        adjusted_value: number;
        value_range: {
            min: number;
            max: number;
        };
        currency: string;
        confidence: number;
    };
    quality: {
        score: number;
        notes: string;
    };
    overall_confidence: number;
    market_context: string;
}

/**
 * Smart Caching System
 * Reduces API calls by caching responses with configurable TTL
 */
interface CacheEntry<T> {
    data: T;
    timestamp: number;
    ttl: number; // Time to live in milliseconds
}

class APICache {
    private cache = new Map<string, CacheEntry<unknown>>();
    private pendingRequests = new Map<string, Promise<unknown>>();

    // Default TTL values (in milliseconds)
    static TTL = {
        SHORT: 30 * 1000,        // 30 seconds - for rapidly changing data
        MEDIUM: 2 * 60 * 1000,   // 2 minutes - for narratives, signals
        LONG: 5 * 60 * 1000,     // 5 minutes - for status, stats
        VERY_LONG: 15 * 60 * 1000, // 15 minutes - for historical data
        HYBRID: 10 * 60 * 1000,  // 10 minutes - for expensive multi-agent calls
    };

    get<T>(key: string): T | null {
        const entry = this.cache.get(key) as CacheEntry<T> | undefined;
        if (!entry) return null;

        const now = Date.now();
        if (now - entry.timestamp > entry.ttl) {
            this.cache.delete(key);
            return null;
        }

        return entry.data;
    }

    set<T>(key: string, data: T, ttl: number): void {
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl,
        });
    }

    // Deduplicate concurrent requests to the same endpoint
    async dedupe<T>(key: string, fetcher: () => Promise<T>, ttl: number): Promise<T> {
        // Check cache first
        const cached = this.get<T>(key);
        if (cached !== null) {
            console.log(`📦 Cache hit: ${key}`);
            return cached;
        }

        // Check if there's already a pending request
        const pending = this.pendingRequests.get(key);
        if (pending) {
            console.log(`⏳ Deduped: ${key}`);
            return pending as Promise<T>;
        }

        // Make the request
        console.log(`🌐 Fetching: ${key}`);
        const promise = fetcher().then((data) => {
            this.set(key, data, ttl);
            this.pendingRequests.delete(key);
            return data;
        }).catch((error) => {
            this.pendingRequests.delete(key);
            throw error;
        });

        this.pendingRequests.set(key, promise);
        return promise;
    }

    // Invalidate specific cache entries
    invalidate(key: string): void {
        this.cache.delete(key);
    }

    // Invalidate all entries matching a pattern
    invalidatePrefix(prefix: string): void {
        for (const key of this.cache.keys()) {
            if (key.startsWith(prefix)) {
                this.cache.delete(key);
            }
        }
    }

    // Clear entire cache
    clear(): void {
        this.cache.clear();
        console.log('🗑️ Cache cleared');
    }

    // Get cache stats
    stats(): { entries: number; keys: string[] } {
        return {
            entries: this.cache.size,
            keys: Array.from(this.cache.keys()),
        };
    }
}

// Global cache instance
const apiCache = new APICache();

// Export for manual cache control
export { apiCache, APICache };

class SilverSentinelAPI {
    
    /**
     * Get current trading signal
     */
    async getTradingSignal(): Promise<TradingSignal | null> {
        return apiCache.dedupe('trading-signal', async () => {
            const res = await fetch(`${API_BASE_URL}/trading-signal`);
            if (!res.ok) throw new Error('Failed to fetch signal');
            return await res.json();
        }, APICache.TTL.MEDIUM);
    }

    /**
     * Get active narratives
     */
    async getNarratives(): Promise<Narrative[]> {
        return apiCache.dedupe('narratives', async () => {
            const res = await fetch(`${API_BASE_URL}/narratives`);
            if (!res.ok) throw new Error('Failed to fetch narratives');
            const data = await res.json();
            return data.narratives || [];
        }, APICache.TTL.MEDIUM);
    }

    /**
     * Get specific narrative details
     */
    async getNarrativeDetails(id: string): Promise<Narrative | null> {
        try {
            const res = await fetch(`${API_BASE_URL}/narratives/${id}`);
            if (!res.ok) throw new Error('Failed to fetch narrative details');
            return await res.json();
        } catch (error) {
            console.error('Error fetching narrative details:', error);
            return null;
        }
    }

    /**
     * Get market stability score
     */
    async getStability(): Promise<MarketStability | null> {
        return apiCache.dedupe('stability', async () => {
            const res = await fetch(`${API_BASE_URL}/stability`);
            if (!res.ok) throw new Error('Failed to fetch stability');
            const data = await res.json();
            return {
                score: data.stability?.score || 0,
                status: data.stability?.status || 'UNKNOWN',
                ...data
            };
        }, APICache.TTL.LONG);
    }

    /**
     * Analyze image using Computer Vision
     */
    async analyzeImage(file: File): Promise<ScanResult | null> {
        const formData = new FormData();
        formData.append('image', file); // Backend expects 'image'

        try {
            const res = await fetch(`${API_BASE_URL}/scan`, {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Failed to analyze image');
            }
            return await res.json();
        } catch (error) {
            console.error('Error analyzing image:', error);
            throw error;
        }
    }
    
     /**
     * Get Price History (New method for chart)
     */
    async getPriceHistory(): Promise<{ timestamp: string, price: number }[]> {
        return apiCache.dedupe('price-history', async () => {
            const res = await fetch(`${API_BASE_URL}/price/history?hours=24`);
            if (!res.ok) throw new Error('Failed to fetch price history');
            const data = await res.json();
            return data.prices || [];
        }, APICache.TTL.SHORT);
    }

    /**
     * Trigger new data collection (manual refresh)
     */
    async collectData(): Promise<boolean> {
        try {
            const res = await fetch(`${API_BASE_URL}/collect-data`, { method: 'POST' });
            return res.ok;
        } catch (error) {
            console.error('Error triggering data collection:', error);
            return false;
        }
    }

    /**
     * Get narrative forecast (48h prediction)
     */
    async getNarrativeForecast(id: string | number): Promise<NarrativeForecast | null> {
        return apiCache.dedupe(`narrative-forecast-${id}`, async () => {
            const res = await fetch(`${API_BASE_URL}/narratives/${id}/forecast`);
            if (!res.ok) throw new Error('Failed to fetch forecast');
            return await res.json();
        }, APICache.TTL.LONG);
    }

    /**
     * Get hybrid analysis with multi-agent debate
     */
    async getHybridAnalysis(id: string | number): Promise<HybridAnalysis | null> {
        // Long cache for expensive multi-agent analysis
        return apiCache.dedupe(`hybrid-analysis-${id}`, async () => {
            const res = await fetch(`${API_BASE_URL}/narratives/${id}/analyze-hybrid`, { method: 'POST' });
            if (!res.ok) throw new Error('Failed to fetch hybrid analysis');
            const data = await res.json();
            return data.data || data;
        }, APICache.TTL.HYBRID);
    }

    /**
     * Get enhanced trading signal with AI reasoning
     */
    async getEnhancedSignal(): Promise<EnhancedSignal | null> {
        return apiCache.dedupe('enhanced-signal', async () => {
            const res = await fetch(`${API_BASE_URL}/trading-signal-enhanced`);
            if (!res.ok) throw new Error('Failed to fetch enhanced signal');
            return await res.json();
        }, APICache.TTL.HYBRID);
    }

    /**
     * Get signal history
     */
    async getSignalHistory(limit: number = 10): Promise<SignalHistoryItem[]> {
        try {
            const res = await fetch(`${API_BASE_URL}/signals/history?limit=${limit}`);
            if (!res.ok) throw new Error('Failed to fetch signal history');
            const data = await res.json();
            return data.signals || [];
        } catch (error) {
            console.error('Error fetching signal history:', error);
            return [];
        }
    }

    /**
     * Get system status
     */
    async getSystemStatus(): Promise<SystemStatus | null> {
        try {
            const res = await fetch(`${API_BASE_URL}/status`);
            if (!res.ok) throw new Error('Failed to fetch status');
            return await res.json();
        } catch (error) {
            console.error('Error fetching system status:', error);
            return null;
        }
    }

    /**
     * Get system statistics
     */
    async getStats(): Promise<SystemStats | null> {
        try {
            const res = await fetch(`${API_BASE_URL}/stats`);
            if (!res.ok) throw new Error('Failed to fetch stats');
            return await res.json();
        } catch (error) {
            console.error('Error fetching stats:', error);
            return null;
        }
    }

    /**
     * Get bias transparency report
     */
    async getBiasReport(): Promise<BiasReport | null> {
        try {
            const res = await fetch(`${API_BASE_URL}/bias/report`);
            if (!res.ok) throw new Error('Failed to fetch bias report');
            return await res.json();
        } catch (error) {
            console.error('Error fetching bias report:', error);
            return null;
        }
    }

    /**
     * Get current silver price
     */
    async getCurrentPrice(): Promise<PriceData | null> {
        try {
            const res = await fetch(`${API_BASE_URL}/price/current`);
            if (!res.ok) throw new Error('Failed to fetch current price');
            return await res.json();
        } catch (error) {
            console.error('Error fetching current price:', error);
            return null;
        }
    }

    /**
     * Get user's scan history
     */
    async getUserScans(userId: string, limit: number = 10): Promise<ScanHistoryItem[]> {
        try {
            const res = await fetch(`${API_BASE_URL}/scans/user/${userId}?limit=${limit}`);
            if (!res.ok) throw new Error('Failed to fetch scan history');
            const data = await res.json();
            return data.scans || [];
        } catch (error) {
            console.error('Error fetching scan history:', error);
            return [];
        }
    }
}

// Additional type definitions
export interface NarrativeForecast {
    narrative_id: number;
    lifecycle_forecast?: {
        current_phase: string;
        next_phase?: string;
        predicted_next_phase?: string;
        probability?: number;
        transition_probability?: number;
        timeframe_hours?: number;
        time_to_transition_hours?: number;
        reasoning?: string;
    };
    price_impact_forecast?: {
        direction: string;
        magnitude?: number;
        magnitude_percentage?: number;
        confidence: number;
    };
    timestamp?: string;
}

export interface AgentVote {
    agent_name: string;
    phase_vote: string;
    strength_vote: number;
    confidence: number;
    reasoning: string;
}

export interface HybridAnalysis {
    consensus_lifecycle_phase: string;
    consensus_strength_score: number;
    overall_confidence: number;
    agent_votes: AgentVote[];
    minority_opinions: {
        agent: string;
        phase: string;
        strength: number;
        reasoning: string;
    }[];
    num_agents: number;
    timestamp: string;
    // From hybrid_engine
    metrics_analysis?: {
        lifecycle_phase: string;
        strength_score: number;
        sources: string[];
    };
}

export interface EnhancedSignal extends TradingSignal {
    agent_insights?: {
        consensus: string;
        minority_opinions: string[];
        agent_confidence: number;
    };
    hybrid_analysis?: {
        method: string;
        metrics: Record<string, number>;
    };
}

export interface SignalHistoryItem {
    id: number;
    action: string;
    confidence: number;
    strength: number;
    reasoning: string;
    timestamp: string;
    price_at_signal: number;
}

export interface OrchestratorStats {
    groq_calls?: number;
    gemini_calls?: number;
    success_rate?: number;
    groq_available?: boolean;
    gemini_available?: boolean;
    [key: string]: unknown;
}

export interface SystemStatus {
    status: string;
    narratives: Record<string, number>;
    orchestrator: OrchestratorStats;
    resource_manager: Record<string, unknown>;
    timestamp: string;
}

export interface SystemStats {
    narratives: { total: number; active: number };
    signals: number;
    prices: number;
    scans: number;
    orchestrator: OrchestratorStats;
    timestamp: string;
}

export interface BiasReport {
    report: {
        region_distribution: Record<string, number>;
        warnings: string[];
        adjustments: Record<string, unknown>[];
    };
    timestamp: string;
}

export interface PriceData {
    price: number;
    timestamp: string;
    source: string;
    currency?: string;
    usd_inr_rate?: number;
}

export interface ScanHistoryItem {
    id: string;
    detected_type: string;
    purity: number;
    weight_g: number;
    valuation_min: number;
    valuation_max: number;
    created_at: string;
}

export const api = new SilverSentinelAPI();

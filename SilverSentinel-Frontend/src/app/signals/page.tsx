"use client";
import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { api, TradingSignal, SignalHistoryItem, EnhancedSignal } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";

const actionColors = {
    BUY: { bg: "bg-lime-500", text: "text-lime-400", ring: "ring-lime-400" },
    SELL: { bg: "bg-red-500", text: "text-red-400", ring: "ring-red-400" },
    HOLD: { bg: "bg-amber-500", text: "text-amber-400", ring: "ring-amber-400" },
};

function SignalGauge({ action, confidence }: { action: string; confidence: number }) {
    const colors = actionColors[action as keyof typeof actionColors] || actionColors.HOLD;
    const circumference = 2 * Math.PI * 90;
    const strokeDashoffset = circumference - (confidence * circumference);

    return (
        <div className="relative w-64 h-64 mx-auto">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
                <circle
                    cx="100"
                    cy="100"
                    r="90"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="12"
                />
                <motion.circle
                    cx="100"
                    cy="100"
                    r="90"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="12"
                    strokeLinecap="round"
                    className={colors.text}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    style={{
                        strokeDasharray: circumference,
                    }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.3, type: "spring" }}
                    className={`text-5xl font-bold ${colors.text}`}
                >
                    {action}
                </motion.span>
                <span className="text-white/60 text-lg mt-1">{(confidence * 100).toFixed(0)}% confident</span>
            </div>
        </div>
    );
}

function SignalHistoryCard({ signal }: { signal: SignalHistoryItem }) {
    const colors = actionColors[signal.action as keyof typeof actionColors] || actionColors.HOLD;
    const date = new Date(signal.timestamp);

    return (
        <div className="flex items-center gap-4 p-4 bg-neutral-900/60 rounded-xl border border-white/5">
            <div className={`w-12 h-12 rounded-full ${colors.bg}/20 flex items-center justify-center`}>
                <span className={`font-bold ${colors.text}`}>{signal.action.charAt(0)}</span>
            </div>
            <div className="flex-1">
                <div className="flex items-center gap-2">
                    <span className={`font-bold ${colors.text}`}>{signal.action}</span>
                    <span className="text-white/40 text-sm">•</span>
                    <span className="text-white/60 text-sm">{(signal.confidence * 100).toFixed(0)}% conf</span>
                </div>
                <p className="text-white/40 text-sm line-clamp-1">{signal.reasoning}</p>
            </div>
            <div className="text-right">
                <p className="text-white/60 text-sm">{date.toLocaleDateString()}</p>
                <p className="text-white/40 text-xs">{date.toLocaleTimeString()}</p>
            </div>
        </div>
    );
}

export default function SignalsPage() {
    const [signal, setSignal] = useState<TradingSignal | null>(null);
    const [enhanced, setEnhanced] = useState<EnhancedSignal | null>(null);
    const [history, setHistory] = useState<SignalHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showEnhanced, setShowEnhanced] = useState(false);

    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const [signalData, historyData] = await Promise.all([
                api.getTradingSignal(),
                api.getSignalHistory(10),
            ]);
            setSignal(signalData);
            setHistory(historyData);
        } catch (err) {
            console.error("Failed to fetch signal data:", err);
            setError("Failed to load trading signals. Please try again.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleEnhanced = async () => {
        if (!enhanced) {
            try {
                const data = await api.getEnhancedSignal();
                setEnhanced(data);
            } catch (err) {
                console.error("Failed to fetch enhanced signal:", err);
            }
        }
        setShowEnhanced(!showEnhanced);
    };

    const currentSignal = signal?.signal;

    // Error state
    if (error && !loading) {
        return (
            <>
                <AppNavbar />
                <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white flex items-center justify-center">
                    <div className="text-center max-w-md">
                        <div className="text-red-400 text-6xl mb-4">!</div>
                        <h2 className="text-2xl font-bold mb-4">Error Loading Signals</h2>
                        <p className="text-white/60 mb-6">{error}</p>
                        <button 
                            onClick={fetchData}
                            className="px-6 py-3 bg-lime-400 text-black font-bold rounded-lg hover:bg-lime-300 transition-colors"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <AppNavbar />
            <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white">
                <div className="container max-w-5xl mx-auto px-6">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-12 text-center"
                    >
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
                            Trading <span className="text-lime-400">Signals</span>
                        </h1>
                        <p className="text-white/60 mt-2 text-lg">
                            AI-generated recommendations based on narrative analysis
                        </p>
                    </motion.div>

                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <div className="animate-spin w-12 h-12 border-4 border-lime-400 border-t-transparent rounded-full" />
                        </div>
                    ) : currentSignal ? (
                        <div className="space-y-8">
                            {/* Main Signal Card */}
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-neutral-900/60 border border-white/10 rounded-3xl p-8"
                            >
                                <SignalGauge action={currentSignal.action} confidence={currentSignal.confidence} />

                                {/* Details Grid */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-white/40 text-sm">Strength</p>
                                        <p className="text-2xl font-bold text-white">{currentSignal.strength}</p>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-white/40 text-sm">Position Size</p>
                                        <p className="text-2xl font-bold text-white">{(currentSignal.position_size * 100).toFixed(0)}%</p>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-white/40 text-sm">Price</p>
                                        <p className="text-2xl font-bold text-lime-400">₹{currentSignal.price?.toFixed(2) || 'N/A'}</p>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-white/40 text-sm">Narrative</p>
                                        <p className="text-lg font-bold text-white truncate">{currentSignal.dominant_narrative || 'None'}</p>
                                    </div>
                                </div>

                                {/* Reasoning */}
                                <div className="mt-6 p-4 bg-white/5 rounded-xl">
                                    <h3 className="text-lg font-bold text-white mb-2">Reasoning</h3>
                                    <p className="text-white/70 leading-relaxed">{currentSignal.reasoning}</p>
                                </div>

                                {/* Enhanced Analysis Toggle */}
                                <button
                                    onClick={handleEnhanced}
                                    className="mt-6 w-full py-3 bg-lime-400/10 border border-lime-400/30 rounded-xl text-lime-400 font-bold hover:bg-lime-400/20 transition-colors"
                                >
                                    {showEnhanced ? 'Hide' : 'Show'} AI Agent Debate
                                </button>

                                {/* Enhanced Analysis */}
                                {showEnhanced && enhanced && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: 'auto' }}
                                        className="mt-6 space-y-4"
                                    >
                                        {/* Agent Consensus Summary */}
                                        {enhanced.agent_insights && (
                                            <div className="p-5 bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/30 rounded-xl">
                                                <h3 className="text-xl font-bold text-purple-400 mb-3 flex items-center gap-2">
                                                    🎯 Final Agent Consensus
                                                </h3>
                                                <p className="text-white/80 text-lg leading-relaxed whitespace-pre-wrap">{enhanced.agent_insights.consensus}</p>
                                                <div className="mt-3 flex items-center gap-4">
                                                    <span className="text-purple-400/60 text-sm">
                                                        Agent Confidence: <span className="text-purple-400 font-bold">{((enhanced.agent_insights.agent_confidence || 0) * 100).toFixed(0)}%</span>
                                                    </span>
                                                </div>
                                            </div>
                                        )}

                                        {/* Hybrid Analysis Metrics */}
                                        {enhanced.hybrid_analysis && (
                                            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
                                                <h3 className="text-lg font-bold text-blue-400 mb-3">📊 Analysis Method: {enhanced.hybrid_analysis.method}</h3>
                                                {enhanced.hybrid_analysis.metrics && (
                                                    <div className="grid grid-cols-3 gap-3">
                                                        {Object.entries(enhanced.hybrid_analysis.metrics).map(([key, value]) => (
                                                            <div key={key} className="bg-white/5 rounded-lg p-3 text-center">
                                                                <p className="text-white/40 text-xs capitalize">{key.replace(/_/g, ' ')}</p>
                                                                <p className="text-white font-bold">{typeof value === 'number' ? value.toFixed(2) : value}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* Minority Opinions */}
                                        {enhanced.agent_insights?.minority_opinions && enhanced.agent_insights.minority_opinions.length > 0 && (
                                            <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-xl">
                                                <h3 className="text-lg font-bold text-orange-400 mb-3 flex items-center gap-2">
                                                    ⚡ Dissenting Agent Opinions ({enhanced.agent_insights.minority_opinions.length})
                                                </h3>
                                                <div className="space-y-3">
                                                    {enhanced.agent_insights.minority_opinions.map((opinion, i) => (
                                                        <div key={i} className="p-3 bg-white/5 rounded-lg">
                                                            <p className="text-white/70 text-sm">{opinion}</p>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                )}
                            </motion.div>

                            {/* Signal History */}
                            <div>
                                <h2 className="text-2xl font-bold text-white mb-4">Signal History</h2>
                                {history.length > 0 ? (
                                    <div className="space-y-3">
                                        {history.map((sig, index) => (
                                            <motion.div
                                                key={sig.id}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: index * 0.05 }}
                                            >
                                                <SignalHistoryCard signal={sig} />
                                            </motion.div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-white/60 text-center py-8">No signal history available</p>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-20">
                            <div className="text-6xl mb-4">📈</div>
                            <h2 className="text-2xl font-bold text-white mb-2">No Signal Available</h2>
                            <p className="text-white/60">Waiting for market data analysis</p>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

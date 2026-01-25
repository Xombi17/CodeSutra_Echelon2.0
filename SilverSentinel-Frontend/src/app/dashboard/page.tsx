"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { api, TradingSignal, Narrative, MarketStability } from "@/lib/api";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import AppNavbar from "@/components/AppNavbar";

// WebSocket URL from environment
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000/ws/live";

export default function DashboardPage() {
    const [signal, setSignal] = useState<TradingSignal | null>(null);
    const [narratives, setNarratives] = useState<Narrative[]>([]);
    const [stability, setStability] = useState<MarketStability | null>(null);
    const [events, setEvents] = useState<string[]>([]);
    const [time, setTime] = useState(new Date().toLocaleTimeString());
    const [priceHistory, setPriceHistory] = useState<{ timestamp: string; price: number }[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const reconnectAttempts = useRef(0);
    const MAX_RECONNECT_ATTEMPTS = 5;

    // NOTE: Demo mode disabled - using real backend data
    // To enable demo mode, uncomment: localStorage.setItem("DEMO_MODE", "true");

    // Fetch data with error handling
    const fetchData = useCallback(async () => {
        try {
            setError(null);
            const [sigData, narData, stabData, historyData] = await Promise.all([
                api.getTradingSignal(),
                api.getNarratives(),
                api.getStability(),
                api.getPriceHistory()
            ]);
            setSignal(sigData);
            setNarratives(narData);
            setStability(stabData);
            setPriceHistory(historyData);
        } catch (err) {
            console.error("Failed to fetch dashboard data:", err);
            setError("Failed to load market data. Please check your connection.");
        } finally {
            setLoading(false);
        }
    }, []);

    // Initial Data Fetch
    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Poll every 30s
        const timeInterval = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);

        return () => {
            clearInterval(interval);
            clearInterval(timeInterval);
        };
    }, [fetchData]);

    // WebSocket Connection with exponential backoff
    useEffect(() => {
        const connectWs = () => {
            if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
                setEvents(prev => ["WebSocket connection failed after max retries", ...prev].slice(0, 5));
                return;
            }

            try {
                const ws = new WebSocket(WS_URL);

                ws.onopen = () => {
                    reconnectAttempts.current = 0; // Reset on successful connection
                    setEvents(prev => [`System connected to live market stream...`, ...prev].slice(0, 5));
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.type === 'log') {
                           setEvents(prev => [data.message, ...prev].slice(0, 5));
                        } else if (data.price) {
                           // Real-time price updates could go here
                        }
                    } catch (parseError) {
                        console.error("Failed to parse WebSocket message:", parseError);
                    }
                };

                ws.onerror = (error) => {
                    console.error("WebSocket error:", error);
                };
                
                ws.onclose = () => {
                    reconnectAttempts.current += 1;
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000); // Exponential backoff, max 30s
                    reconnectTimeoutRef.current = setTimeout(connectWs, delay);
                };

                wsRef.current = ws;
            } catch (err) {
                console.error("WebSocket connection error:", err);
            }
        };

        connectWs();
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            wsRef.current?.close();
        };
    }, []);

    // Error state display
    if (error && !loading) {
        return (
            <>
                <AppNavbar />
                <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white flex items-center justify-center">
                    <div className="text-center max-w-md">
                        <div className="text-red-400 text-6xl mb-4">!</div>
                        <h2 className="text-2xl font-bold mb-4">Connection Error</h2>
                        <p className="text-white/60 mb-6">{error}</p>
                        <button 
                            onClick={() => { setLoading(true); fetchData(); }}
                            className="px-6 py-3 bg-lime-400 text-black font-bold rounded-lg hover:bg-lime-300 transition-colors"
                        >
                            Retry Connection
                        </button>
                    </div>
                </div>
            </>
        );
    }

    // Loading state
    if (loading) {
        return (
            <>
                <AppNavbar />
                <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white flex items-center justify-center">
                    <div className="text-center">
                        <div className="animate-spin w-12 h-12 border-4 border-lime-400 border-t-transparent rounded-full mx-auto mb-4" />
                        <p className="text-white/60">Loading market intelligence...</p>
                    </div>
                </div>
            </>
        );
    }


    return (
        <>
            <AppNavbar />
            <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white selection:bg-lime-400 selection:text-black">
            <div className="container max-w-none px-6 md:px-12">
                {/* Institutional Header */}
                <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-12 border-b border-white/5 pb-12">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="size-2 rounded-full bg-lime-400 animate-pulse shadow-[0_0_10px_rgba(163,230,53,0.5)]" />
                            <span className="text-lime-400 text-xs font-bold uppercase tracking-[0.2em]">Live Telemetry Active</span>
                        </div>
                        <h1 className="text-5xl font-bold tracking-tight">Market Intelligence <span className="text-white/30">v4.2</span></h1>
                    </div>
                    <div className="flex gap-8 text-right font-mono">
                        <div className="flex flex-col">
                            <span className="text-[10px] text-white/30 uppercase tracking-widest mb-1">System Time</span>
                            <span className="text-xl font-medium" suppressHydrationWarning>{time}</span>
                        </div>
                        <div className="flex flex-col">
                            <span className="text-[10px] text-white/30 uppercase tracking-widest mb-1">Server Cluster</span>
                            <span className="text-xl font-medium">US-EAST-1</span>
                        </div>
                    </div>
                </div>

                {/* KPI Ribbon */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-white/5 border border-white/5 rounded-2xl overflow-hidden mb-12">
                    <div className="bg-neutral-950 p-8 border-r border-white/5">
                        <span className="text-[10px] text-white/20 uppercase tracking-widest font-bold mb-4 block">Live Market Price</span>
                        <div className="flex items-baseline gap-3">
                            <span className="text-4xl font-bold tracking-tighter text-white">
                                {priceHistory.length > 0 
                                    ? `₹${priceHistory[priceHistory.length - 1].price.toFixed(2)}` 
                                    : '---'}
                            </span>
                            <span className="text-[10px] font-mono text-lime-400/50">/G</span>
                        </div>
                    </div>
                    <div className="bg-neutral-950 p-8">
                        <span className="text-[10px] text-white/20 uppercase tracking-widest font-bold mb-4 block">Trading Signal</span>
                        <div className="flex items-baseline gap-3">
                            <span className={cn("text-4xl font-bold tracking-tighter", 
                                signal?.signal.action === 'BUY' ? "text-lime-400" : 
                                signal?.signal.action === 'SELL' ? "text-red-400" : "text-white")}>
                                {signal ? signal.signal.action : 'WAIT'}
                            </span>
                            <span className="text-[10px] font-mono text-lime-400/50">{signal ? `${signal.signal.strength}% STR` : '...'}</span>
                        </div>
                    </div>
                    <div className="bg-neutral-950 p-8">
                        <span className="text-[10px] text-white/20 uppercase tracking-widest font-bold mb-4 block">AI Confidence</span>
                        <div className="flex items-baseline gap-3">
                            <span className="text-4xl font-bold tracking-tighter text-lime-400">{signal ? ((signal.signal.confidence || 0) * 100).toFixed(1) : '0.0'}%</span>
                             <span className="text-[10px] font-mono text-lime-400/50">MODEL</span>
                        </div>
                    </div>
                     <div className="bg-neutral-950 p-8">
                        <span className="text-[10px] text-white/20 uppercase tracking-widest font-bold mb-4 block">Stability Index</span>
                        <div className="flex items-baseline gap-3">
                            <span className="text-4xl font-bold tracking-tighter text-white/50">{stability ? stability.score : 'PS-14'}</span>
                            <span className="text-[10px] font-mono text-lime-400/50">{stability ? stability.status : 'CALC'}</span>
                        </div>
                    </div>
                </div>

                <div className="grid lg:grid-cols-12 gap-8">
                    {/* Main Intelligence View */}
                    <div className="lg:col-span-8 space-y-8">
                        {/* Interactive Narrative Chart */}
                        <div className="bg-neutral-900/40 border border-white/5 rounded-2xl p-8 relative overflow-hidden h-[400px]">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg font-bold">Price Action Correlation</h3>
                                <div className="flex gap-2">
                                    <div className="px-2 py-1 rounded bg-white/5 text-[10px] font-bold border border-white/10 uppercase">1H</div>
                                    <div className="px-2 py-1 rounded bg-lime-400 text-black text-[10px] font-bold border border-lime-400 uppercase">24H</div>
                                </div>
                            </div>

                            <div className="h-[300px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={priceHistory}>
                                        <defs>
                                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#a3e635" stopOpacity={0.1}/>
                                                <stop offset="95%" stopColor="#a3e635" stopOpacity={0}/>
                                            </linearGradient>
                                        </defs>
                                        <XAxis 
                                            dataKey="timestamp" 
                                            hide 
                                        />
                                        <YAxis 
                                            domain={['auto', 'auto']} 
                                            orientation="right" 
                                            tick={{fill: '#404040', fontSize: 10}} 
                                            axisLine={false}
                                            tickLine={false}
                                        />
                                        <Tooltip 
                                            contentStyle={{backgroundColor: '#0a0a0a', border: '1px solid #333', borderRadius: '8px'}}
                                            itemStyle={{color: '#a3e635', fontSize: '12px', fontWeight: 'bold'}}
                                            labelStyle={{display: 'none'}}
                                            formatter={(value: string | number | undefined) => [value ? `₹${Number(value).toFixed(2)}` : 'N/A', 'Price']}
                                        />
                                        <Area 
                                            type="monotone" 
                                            dataKey="price" 
                                            stroke="#a3e635" 
                                            strokeWidth={2}
                                            fillOpacity={1} 
                                            fill="url(#colorPrice)" 
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Narratives Table */}
                        <div className="bg-neutral-900/40 border border-white/5 rounded-2xl p-8">
                            <h3 className="text-lg font-bold mb-8">Active Narratives Overview</h3>
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead>
                                        <tr className="text-[10px] text-white/20 uppercase tracking-widest border-b border-white/5 pb-4">
                                            <th className="pb-4">Narrative Source</th>
                                            <th className="pb-4">Cluster Phase</th>
                                            <th className="pb-4 text-right">Momentum</th>
                                            <th className="pb-4 text-right">Risk Factor</th>
                                        </tr>
                                    </thead>
                                    <tbody className="text-sm">
                                        {narratives.length === 0 ? (
                                             <tr className="border-b border-white/5 text-white/50">
                                                <td colSpan={4} className="py-4 text-center">Initializing narrative discovery...</td>
                                            </tr>
                                        ) : narratives.map((n, i) => (
                                            <tr key={i} className="border-b border-white/5 group hover:bg-white/5 transition-colors cursor-default">
                                                <td className="py-4 font-medium group-hover:text-lime-400 transition-colors">{n.name}</td>
                                                <td className="py-4"><span className="px-2 py-0.5 rounded-full border border-white/10 text-[9px] font-bold">{n.phase}</span></td>
                                                <td className="py-4 text-right font-mono text-lime-400/80">{n.strength}</td>
                                                <td className="py-4 text-right font-mono opacity-50">{n.risk_score || 0}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    {/* Sidebar Intelligence */}
                    <div className="lg:col-span-4 space-y-8">
                         {/* Decision reasoning */}
                         <div className="bg-lime-400 text-neutral-950 rounded-2xl p-8 shadow-[0_0_40px_rgba(190,255,0,0.1)]">
                            <span className="text-[10px] font-bold uppercase tracking-widest opacity-50 mb-4 block">Signal Reasoning</span>
                            <p className="text-2xl font-bold leading-tight mb-6 tracking-tight">
                                &quot;{signal ? signal.signal.reasoning : "Awaiting autonomous decision..."}&quot;
                            </p>
                            <div className="h-1 w-full bg-black/10 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: signal ? `${signal.signal.confidence * 100}%` : "0%" }}
                                    transition={{ duration: 1 }}
                                    className="h-full bg-neutral-950"
                                />
                            </div>
                            <span className="text-[10px] font-bold mt-2 block opacity-50">CONFIDENCE: {signal ? (signal.signal.confidence * 100).toFixed(0) : 0}%</span>
                        </div>

                        {/* Live Log */}
                        <div className="bg-black/40 border border-white/5 rounded-2xl p-8 font-mono text-xs overflow-hidden h-[400px] flex flex-col">
                            <h3 className="text-white/30 uppercase tracking-widest font-bold mb-6">Autonomous Log</h3>
                            <div className="flex-1 space-y-4">
                                <AnimatePresence mode="popLayout">
                                    {events.map((event, i) => (
                                        <motion.div
                                            key={event + i}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, x: 10 }}
                                            className="flex gap-4 border-l-2 border-lime-400/20 pl-4 py-2"
                                        >
                                            <span className="text-lime-400 font-bold tracking-tighter shrink-0">{new Date().toLocaleTimeString([], { hour12: false })}</span>
                                            <span className="text-white/60 leading-relaxed">{event}</span>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            </div>
        </>
    );
}

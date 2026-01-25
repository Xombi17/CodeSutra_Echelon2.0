import React, { useState, useEffect } from "react";
import Tag from "@/components/Tag";
import { cn } from "@/lib/utils";
import { api, TradingSignal } from "@/lib/api";

export default function Dashboard() {
    const [signal, setSignal] = useState<TradingSignal | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchData() {
            try {
                const signalData = await api.getTradingSignal();
                setSignal(signalData);
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    const displaySignal = signal || {
        signal: {
            action: "HOLD",
            confidence: 0,
            strength: 0,
            reasoning: "Awaiting data...",
            position_size: 0,
            dominant_narrative: "N/A",
            price: 0,
            conflicts: 0
        }
    };

    return (
        <section className="py-24 min-h-screen bg-black/50 relative overflow-hidden" id="dashboard">
            <div className="container max-w-none px-6 md:px-12">
                <div className="mb-12">
                    <Tag>Live Intel</Tag>
                    <h2 className="text-4xl md:text-5xl font-bold mt-6">Market Intelligence Overview</h2>
                </div>

                {/* Metrics Header */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16">
                    <div className="flex flex-col gap-2">
                        <span className="text-white/30 text-sm uppercase tracking-widest font-bold">Active Narratives</span>
                        <span className="text-5xl font-bold">{loading ? "..." : "05"}</span>
                    </div>
                    <div className="flex flex-col gap-2">
                        <span className="text-white/30 text-sm uppercase tracking-widest font-bold">Trading Signal</span>
                        <div className="flex items-center gap-3">
                            <div className={cn(
                                "size-8 rounded-full shadow-[0_0_20px_rgba(234,179,8,0.5)] border-2 animate-pulse",
                                displaySignal.signal.action === "BUY" ? "bg-lime-500 border-lime-300" :
                                displaySignal.signal.action === "SELL" ? "bg-red-500 border-red-300" : "bg-yellow-500 border-yellow-300"
                            )} />
                            <span className="text-5xl font-bold">{displaySignal.signal.action}</span>
                        </div>
                    </div>
                    <div className="flex flex-col gap-2">
                        <span className="text-white/30 text-sm uppercase tracking-widest font-bold">Confidence</span>
                        <span className="text-5xl font-bold text-lime-400">{(displaySignal.signal.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex flex-col gap-2">
                        <span className="text-white/30 text-sm uppercase tracking-widest font-bold">Current Price</span>
                        <span className="text-5xl font-bold text-white/50">
                            ₹{displaySignal.signal.price ? displaySignal.signal.price.toFixed(2) : "---"}
                        </span>
                    </div>
                </div>

                {/* Content Grid */}
                <div className="grid lg:grid-cols-2 gap-12">
                    {/* Narratives Table (Placeholder for live narratives) */}
                    <div className="bg-neutral-900/40 border border-white/10 rounded-3xl p-8 overflow-x-auto">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="size-3 rounded shadow-[0_0_10px_#fff] bg-white" />
                            <h3 className="text-2xl font-bold">Top Active Narratives</h3>
                        </div>
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-white/5 text-white/30 text-xs uppercase tracking-widest">
                                    <th className="pb-4 font-bold">Narrative</th>
                                    <th className="pb-4 font-bold">Phase</th>
                                    <th className="pb-4 font-bold text-center">Strength</th>
                                    <th className="pb-4 font-bold text-center">Impact</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    { name: "Industrial Solar Demand", phase: "growth", strength: 82, impact: "+4.2%" },
                                    { name: "Mining Strike (South Africa)", phase: "peak", strength: 91, impact: "+6.8%" },
                                    { name: "Wedding Season Demand", phase: "growth", strength: 65, impact: "+2.1%" },
                                ].map((item, i) => (
                                    <tr key={i} className="border-b border-white/5 group hover:bg-white/5 transition-colors">
                                        <td className="py-4 font-medium">{item.name}</td>
                                        <td className="py-4">
                                            <span className={cn(
                                                "px-2 py-1 rounded text-[10px] uppercase font-bold border",
                                                item.phase === "growth" && "text-lime-400 border-lime-400/30 bg-lime-400/10",
                                                item.phase === "peak" && "text-yellow-400 border-yellow-400/30 bg-yellow-400/10"
                                            )}>
                                                {item.phase}
                                            </span>
                                        </td>
                                        <td className="py-4 text-center font-mono">{item.strength}</td>
                                        <td className="py-4 text-center font-mono opacity-50">{item.impact}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Trading Signal JSON View */}
                    <div className="bg-neutral-900/40 border border-white/10 rounded-3xl p-8 flex flex-col h-full">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="size-3 rounded shadow-[0_0_10px_#fff] bg-white" />
                            <h3 className="text-2xl font-bold">Current Trading Signal</h3>
                        </div>
                        <div className="flex-1 bg-black/40 rounded-xl p-6 font-mono text-sm border border-white/5 relative overflow-hidden group">
                            {/* Decorative scan line */}
                            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-lime-500/5 to-transparent h-full w-full -translate-y-full group-hover:animate-[scan_3s_linear_infinite]" />

                            <pre className="text-lime-400/90 whitespace-pre-wrap">
                                {JSON.stringify(displaySignal.signal, null, 4)}
                            </pre>

                            <div className="mt-8 p-4 bg-lime-400/10 border border-lime-400/20 rounded-lg">
                                <p className="text-lime-400 text-xs uppercase tracking-widest font-bold mb-2">Internal Reasoning</p>
                                <p className="text-lg font-medium text-white/80 italic leading-relaxed">
                                    &quot;{displaySignal.signal.reasoning}&quot;
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx>{`
                @keyframes scan {
                    0% { transform: translateY(-100%); }
                    100% { transform: translateY(100%); }
                }
            `}</style>
        </section>
    );
}

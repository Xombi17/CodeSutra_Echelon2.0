"use client";

import Navbar from "@/sections/Navbar";
import { use, useState, useEffect } from "react";
import { api, Narrative } from "@/lib/api";
import Link from "next/link";

export default function NarrativePage({ params }: { params: Promise<{ id: string }> }) {
    const unwrappedParams = use(params);
    const { id } = unwrappedParams;
    const [narrative, setNarrative] = useState<Narrative | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNarrative = async () => {
            if (id) {
                const data = await api.getNarrativeDetails(id);
                setNarrative(data);
                setLoading(false);
            }
        };
        fetchNarrative();
    }, [id]);

    if (loading) {
         return (
             <>
                <Navbar />
                <div className="min-h-screen pt-32 pb-20 flex items-center justify-center bg-neutral-950 text-white">
                    <p className="animate-pulse">Accessing Intelligence Database...</p>
                </div>
            </>
        );
    }

    if (!narrative) {
        return (
             <>
                <Navbar />
                <div className="min-h-screen pt-32 pb-20 flex items-center justify-center bg-neutral-950 text-white">
                    <div className="text-center">
                        <h1 className="text-3xl font-bold mb-4">Narrative Not Found</h1>
                        <p className="text-white/60">The story you are looking for does not exist or has been archived.</p>
                        <Link href="/dashboard" className="mt-8 inline-block text-lime-400 hover:underline">Return to Dashboard</Link>
                    </div>
                </div>
            </>
        );
    }

    return (
        <>
            <Navbar />
            <section className="pt-32 pb-20 min-h-screen bg-neutral-950 text-white selection:bg-lime-400 selection:text-black">
                <div className="container mx-auto px-4">
                    <div className="max-w-4xl mx-auto">
                        <div className="mb-8">
                             <Link href="/dashboard" className="text-white/40 hover:text-white transition-colors flex items-center gap-2 mb-4">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                                Back to Dashboard
                            </Link>
                            <div className="flex items-start justify-between gap-4">
                                <h1 className="text-4xl md:text-5xl font-bold leading-tight">
                                    {narrative.name}
                                </h1>
                                <span className={`px-4 py-1 rounded-full text-sm font-medium border ${
                                    (narrative.sentiment || 0) > 0
                                        ? 'bg-lime-400/10 text-lime-400 border-lime-400/20' 
                                        : 'bg-red-500/10 text-red-400 border-red-500/20'
                                }`}>
                                    {(narrative.sentiment || 0) > 0.1 ? 'Bullish' : (narrative.sentiment || 0) < -0.1 ? 'Bearish' : 'Neutral'}
                                </span>
                            </div>
                        </div>

                        <div className="grid md:grid-cols-3 gap-8">
                            <div className="md:col-span-2 space-y-8">
                                <div className="glass-panel p-8 rounded-3xl border border-white/5 bg-white/5">
                                    <h2 className="text-2xl font-semibold mb-4">Executive Summary</h2>
                                    <p className="text-lg text-white/80 leading-relaxed">
                                        {narrative.description || "No description available for this narrative. It has been identified through autonomous clustering of market signals."}
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-6">
                                <div className="glass-panel p-6 rounded-3xl border border-white/5 bg-white/5">
                                    <h3 className="text-sm text-white/50 uppercase tracking-wider mb-1">Impact Score</h3>
                                    <div className="flex items-end gap-2">
                                        <span className="text-5xl font-bold text-white">{narrative.strength}</span>
                                        <span className="text-xl text-white/40 mb-1">/100</span>
                                    </div>
                                    <div className="w-full h-1.5 bg-white/10 rounded-full mt-4 overflow-hidden">
                                        <div 
                                            className="h-full bg-gradient-to-r from-lime-400 to-lime-300"
                                            style={{ width: `${narrative.strength}%` }}
                                        />
                                    </div>
                                </div>

                                <div className="glass-panel p-6 rounded-3xl border border-white/5 bg-white/5">
                                    <h3 className="text-sm text-white/50 uppercase tracking-wider mb-2">Metadata</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <p className="text-xs text-white/40">Detected On</p>
                                            <p className="font-medium">{narrative.last_updated ? new Date(narrative.last_updated).toLocaleDateString() : 'Recently'}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-white/40">Status</p>
                                            <p className="font-medium capitalize">{narrative.phase}</p>
                                        </div>
                                         <div>
                                            <p className="text-xs text-white/40">Article Count</p>
                                            <p className="font-medium">{narrative.article_count || 0}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}

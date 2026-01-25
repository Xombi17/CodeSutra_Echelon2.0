"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api, SystemStatus, SystemStats, BiasReport, MarketStability } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";

function StabilityGauge({ score, status }: { score: number; status: string }) {
    const getColor = (score: number) => {
        if (score >= 80) return { text: "text-lime-400", bg: "bg-lime-400" };
        if (score >= 60) return { text: "text-green-400", bg: "bg-green-400" };
        if (score >= 40) return { text: "text-amber-400", bg: "bg-amber-400" };
        if (score >= 20) return { text: "text-orange-400", bg: "bg-orange-400" };
        return { text: "text-red-400", bg: "bg-red-400" };
    };
    const colors = getColor(score);

    return (
        <div className="relative w-48 h-48">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="8"
                />
                <motion.circle
                    cx="50"
                    cy="50"
                    r="45"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="8"
                    strokeLinecap="round"
                    className={colors.text}
                    initial={{ strokeDashoffset: 283 }}
                    animate={{ strokeDashoffset: 283 - (score / 100) * 283 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    style={{ strokeDasharray: 283 }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-4xl font-bold ${colors.text}`}>{score}</span>
                <span className="text-white/60 text-sm uppercase">{status}</span>
            </div>
        </div>
    );
}

function PhaseDistribution({ phases }: { phases: Record<string, number> }) {
    const total = Object.values(phases).reduce((a, b) => a + b, 0) || 1;
    const phaseColors: Record<string, string> = {
        birth: "bg-blue-400",
        growth: "bg-lime-400",
        peak: "bg-amber-400",
        reversal: "bg-orange-400",
        death: "bg-red-400",
    };

    return (
        <div className="space-y-3">
            {Object.entries(phases).map(([phase, count]) => (
                <div key={phase}>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-white/60 capitalize">{phase}</span>
                        <span className="text-white font-bold">{count}</span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(count / total) * 100}%` }}
                            transition={{ duration: 0.8 }}
                            className={`h-full rounded-full ${phaseColors[phase] || 'bg-gray-400'}`}
                        />
                    </div>
                </div>
            ))}
        </div>
    );
}

function BiasWarnings({ report }: { report: BiasReport['report'] }) {
    if (!report?.warnings?.length) {
        return (
            <div className="p-4 bg-lime-400/10 border border-lime-400/30 rounded-xl">
                <div className="flex items-center gap-2">
                    <span className="text-lime-400">✓</span>
                    <span className="text-lime-400 font-bold">No Geographic Bias Detected</span>
                </div>
                <p className="text-white/60 text-sm mt-1">Data sources are well-distributed globally</p>
            </div>
        );
    }

    return (
        <div className="space-y-2">
            {report.warnings.map((warning, i) => (
                <div key={i} className="p-3 bg-amber-400/10 border border-amber-400/30 rounded-xl">
                    <div className="flex items-start gap-2">
                        <span className="text-amber-400">⚠</span>
                        <span className="text-amber-400 text-sm">{warning}</span>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default function StatusPage() {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [stats, setStats] = useState<SystemStats | null>(null);
    const [stability, setStability] = useState<MarketStability | null>(null);
    const [bias, setBias] = useState<BiasReport | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            const [statusData, statsData, stabilityData, biasData] = await Promise.all([
                api.getSystemStatus(),
                api.getStats(),
                api.getStability(),
                api.getBiasReport(),
            ]);
            setStatus(statusData);
            setStats(statsData);
            setStability(stabilityData);
            setBias(biasData);
            setLoading(false);
        };
        fetchData();
    }, []);

    return (
        <>
            <AppNavbar />
            <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white">
                <div className="container max-w-6xl mx-auto px-6">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-12"
                    >
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
                            System <span className="text-lime-400">Status</span>
                        </h1>
                        <p className="text-white/60 mt-2 text-lg">
                            Monitor system health, market stability, and data transparency
                        </p>
                    </motion.div>

                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <div className="animate-spin w-12 h-12 border-4 border-lime-400 border-t-transparent rounded-full" />
                        </div>
                    ) : (
                        <div className="grid lg:grid-cols-3 gap-6">
                            {/* Stability Gauge */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="lg:col-span-1 bg-neutral-900/60 border border-white/10 rounded-3xl p-6 flex flex-col items-center"
                            >
                                <h2 className="text-xl font-bold text-white mb-4">Market Stability</h2>
                                <StabilityGauge 
                                    score={stability?.stability?.score || stability?.score || 0} 
                                    status={stability?.stability?.status || stability?.status || 'Unknown'} 
                                />
                                <div className="mt-4 text-center">
                                    <p className="text-white/60 text-sm">
                                        {stability?.stability?.consecutive_stable_days || 0} consecutive stable days
                                    </p>
                                </div>
                            </motion.div>

                            {/* System Stats */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="lg:col-span-2 bg-neutral-900/60 border border-white/10 rounded-3xl p-6"
                            >
                                <h2 className="text-xl font-bold text-white mb-4">System Statistics</h2>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-3xl font-bold text-lime-400">{stats?.narratives?.active || 0}</p>
                                        <p className="text-white/60 text-sm">Active Narratives</p>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-3xl font-bold text-white">{stats?.narratives?.total || 0}</p>
                                        <p className="text-white/60 text-sm">Total Narratives</p>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-3xl font-bold text-white">{stats?.signals || 0}</p>
                                        <p className="text-white/60 text-sm">Signals Generated</p>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4 text-center">
                                        <p className="text-3xl font-bold text-white">{stats?.scans || 0}</p>
                                        <p className="text-white/60 text-sm">Scans Completed</p>
                                    </div>
                                </div>

                                {/* Orchestrator Status */}
                                {stats?.orchestrator && (
                                    <div className="mt-6 grid grid-cols-3 gap-4">
                                        <div className="bg-white/5 rounded-xl p-3 text-center">
                                            <p className="text-lg font-bold text-purple-400">{stats.orchestrator.groq_calls || 0}</p>
                                            <p className="text-white/40 text-xs">Groq API Calls</p>
                                        </div>
                                        <div className="bg-white/5 rounded-xl p-3 text-center">
                                            <p className="text-lg font-bold text-blue-400">{stats.orchestrator.gemini_calls || 0}</p>
                                            <p className="text-white/40 text-xs">Gemini Calls</p>
                                        </div>
                                        <div className="bg-white/5 rounded-xl p-3 text-center">
                                            <p className="text-lg font-bold text-green-400">{((stats.orchestrator.success_rate || 0) * 100).toFixed(0)}%</p>
                                            <p className="text-white/40 text-xs">Success Rate</p>
                                        </div>
                                    </div>
                                )}
                            </motion.div>

                            {/* Narrative Phase Distribution */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                                className="bg-neutral-900/60 border border-white/10 rounded-3xl p-6"
                            >
                                <h2 className="text-xl font-bold text-white mb-4">Narrative Phases</h2>
                                {status?.narratives && <PhaseDistribution phases={status.narratives} />}
                            </motion.div>

                            {/* Geographic Bias Transparency */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.3 }}
                                className="lg:col-span-2 bg-neutral-900/60 border border-white/10 rounded-3xl p-6"
                            >
                                <h2 className="text-xl font-bold text-white mb-4">Data Transparency</h2>
                                <p className="text-white/60 text-sm mb-4">
                                    Geographic bias detection ensures balanced global coverage
                                </p>
                                {bias && <BiasWarnings report={bias.report} />}

                                {bias?.report?.region_distribution && (
                                    <div className="mt-6">
                                        <h3 className="text-sm font-bold text-white/60 mb-3">Region Distribution</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {Object.entries(bias.report.region_distribution).map(([region, count]) => (
                                                <span
                                                    key={region}
                                                    className="px-3 py-1 bg-white/5 rounded-full text-sm text-white/70"
                                                >
                                                    {region}: {count as number}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </motion.div>

                            {/* System Health */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.4 }}
                                className="lg:col-span-3 bg-neutral-900/60 border border-white/10 rounded-3xl p-6"
                            >
                                <h2 className="text-xl font-bold text-white mb-4">Service Health</h2>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className={`p-4 rounded-xl border ${status?.status === 'operational' ? 'bg-lime-400/10 border-lime-400/30' : 'bg-red-400/10 border-red-400/30'}`}>
                                        <div className="flex items-center gap-2">
                                            <div className={`w-3 h-3 rounded-full ${status?.status === 'operational' ? 'bg-lime-400' : 'bg-red-400'} animate-pulse`} />
                                            <span className="font-bold text-white">API Server</span>
                                        </div>
                                        <p className="text-white/60 text-sm mt-1 capitalize">{status?.status || 'Unknown'}</p>
                                    </div>
                                    <div className="p-4 rounded-xl border bg-lime-400/10 border-lime-400/30">
                                        <div className="flex items-center gap-2">
                                            <div className="w-3 h-3 rounded-full bg-lime-400 animate-pulse" />
                                            <span className="font-bold text-white">Database</span>
                                        </div>
                                        <p className="text-white/60 text-sm mt-1">Connected</p>
                                    </div>
                                    <div className={`p-4 rounded-xl border ${stats?.orchestrator?.groq_available ? 'bg-lime-400/10 border-lime-400/30' : 'bg-amber-400/10 border-amber-400/30'}`}>
                                        <div className="flex items-center gap-2">
                                            <div className={`w-3 h-3 rounded-full ${stats?.orchestrator?.groq_available ? 'bg-lime-400' : 'bg-amber-400'}`} />
                                            <span className="font-bold text-white">Groq AI</span>
                                        </div>
                                        <p className="text-white/60 text-sm mt-1">{stats?.orchestrator?.groq_available ? 'Available' : 'Rate Limited'}</p>
                                    </div>
                                    <div className={`p-4 rounded-xl border ${stats?.orchestrator?.gemini_available ? 'bg-lime-400/10 border-lime-400/30' : 'bg-red-400/10 border-red-400/30'}`}>
                                        <div className="flex items-center gap-2">
                                            <div className={`w-3 h-3 rounded-full ${stats?.orchestrator?.gemini_available ? 'bg-lime-400' : 'bg-red-400'}`} />
                                            <span className="font-bold text-white">Gemini Vision</span>
                                        </div>
                                        <p className="text-white/60 text-sm mt-1">{stats?.orchestrator?.gemini_available ? 'Available' : 'Unavailable'}</p>
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

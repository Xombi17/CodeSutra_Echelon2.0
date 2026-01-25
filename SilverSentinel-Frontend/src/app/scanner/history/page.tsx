"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api, ScanHistoryItem } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";
import Link from "next/link";

const typeIcons: Record<string, string> = {
    bracelet: "💍",
    ring: "💍",
    chain: "📿",
    necklace: "📿",
    coin: "🪙",
    bar: "🏅",
    jewelry: "✨",
    unknown: "🔍",
};

function ScanCard({ scan }: { scan: ScanHistoryItem }) {
    const icon = typeIcons[scan.detected_type?.toLowerCase()] || typeIcons.unknown;
    const date = new Date(scan.created_at);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
            className="bg-neutral-900/60 border border-white/10 rounded-2xl p-6 cursor-pointer hover:border-lime-400/30 transition-all"
        >
            <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-lime-400/10 rounded-xl flex items-center justify-center text-3xl">
                    {icon}
                </div>
                <div className="flex-1">
                    <div className="flex justify-between items-start">
                        <div>
                            <h3 className="text-lg font-bold text-white capitalize">{scan.detected_type || 'Silver Object'}</h3>
                            <p className="text-white/40 text-sm">{date.toLocaleDateString()} at {date.toLocaleTimeString()}</p>
                        </div>
                        <span className="px-3 py-1 bg-lime-400/10 border border-lime-400/30 rounded-full text-lime-400 text-xs font-bold">
                            {scan.purity ? `${(scan.purity / 10).toFixed(1)}%` : 'N/A'}
                        </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mt-4">
                        <div>
                            <p className="text-white/40 text-xs">Weight</p>
                            <p className="text-white font-bold">{scan.weight_g?.toFixed(1) || '?'}g</p>
                        </div>
                        <div>
                            <p className="text-white/40 text-xs">Valuation Range</p>
                            <p className="text-lime-400 font-bold">
                                ₹{scan.valuation_min?.toLocaleString('en-IN') || '?'} - ₹{scan.valuation_max?.toLocaleString('en-IN') || '?'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

export default function ScannerHistoryPage() {
    const [scans, setScans] = useState<ScanHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Get user ID from localStorage or use anonymous
        const storedUserId = localStorage.getItem("userId") || "anonymous";

        const fetchScans = async () => {
            setLoading(true);
            const data = await api.getUserScans(storedUserId, 20);
            setScans(data);
            setLoading(false);
        };
        fetchScans();
    }, []);

    // Calculate totals
    const totalValue = scans.reduce((sum, scan) => sum + ((scan.valuation_min + scan.valuation_max) / 2), 0);
    const totalWeight = scans.reduce((sum, scan) => sum + (scan.weight_g || 0), 0);

    return (
        <>
            <AppNavbar />
            <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white">
                <div className="container max-w-5xl mx-auto px-6">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8"
                    >
                        <div className="flex justify-between items-start">
                            <div>
                                <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
                                    Scan <span className="text-lime-400">History</span>
                                </h1>
                                <p className="text-white/60 mt-2 text-lg">
                                    Your scanned silver items and valuations
                                </p>
                            </div>
                            <Link
                                href="/scanner"
                                className="px-6 py-3 bg-lime-400 text-black font-bold rounded-xl hover:bg-lime-300 transition-colors"
                            >
                                + New Scan
                            </Link>
                        </div>
                    </motion.div>

                    {/* Summary Stats */}
                    {scans.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="grid grid-cols-3 gap-4 mb-8"
                        >
                            <div className="bg-neutral-900/60 border border-white/10 rounded-2xl p-6 text-center">
                                <p className="text-white/60 text-sm">Total Scans</p>
                                <p className="text-3xl font-bold text-white">{scans.length}</p>
                            </div>
                            <div className="bg-neutral-900/60 border border-white/10 rounded-2xl p-6 text-center">
                                <p className="text-white/60 text-sm">Total Weight</p>
                                <p className="text-3xl font-bold text-white">{totalWeight.toFixed(1)}g</p>
                            </div>
                            <div className="bg-gradient-to-br from-lime-400/10 to-transparent border border-lime-400/30 rounded-2xl p-6 text-center">
                                <p className="text-lime-400/80 text-sm">Est. Portfolio Value</p>
                                <p className="text-3xl font-bold text-lime-400">₹{totalValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                            </div>
                        </motion.div>
                    )}

                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <div className="animate-spin w-12 h-12 border-4 border-lime-400 border-t-transparent rounded-full" />
                        </div>
                    ) : scans.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center py-20"
                        >
                            <div className="text-6xl mb-4">📷</div>
                            <h2 className="text-2xl font-bold text-white mb-2">No Scans Yet</h2>
                            <p className="text-white/60 mb-6">Start scanning your silver items to build your portfolio</p>
                            <Link
                                href="/scanner"
                                className="inline-block px-8 py-4 bg-lime-400 text-black font-bold rounded-xl hover:bg-lime-300 transition-colors"
                            >
                                Scan Your First Item
                            </Link>
                        </motion.div>
                    ) : (
                        <div className="space-y-4">
                            {scans.map((scan, index) => (
                                <motion.div
                                    key={scan.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.05 }}
                                >
                                    <ScanCard scan={scan} />
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

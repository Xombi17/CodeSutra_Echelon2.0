"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api, PriceData } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from "recharts";

type TimeRange = "1H" | "24H" | "7D" | "30D";

export default function AnalyticsPage() {
    const [currentPrice, setCurrentPrice] = useState<PriceData | null>(null);
    const [priceHistory, setPriceHistory] = useState<{ timestamp: string; price: number }[]>([]);
    const [timeRange, setTimeRange] = useState<TimeRange>("24H");
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            const [priceData, history] = await Promise.all([
                api.getCurrentPrice(),
                api.getPriceHistory(),
            ]);
            setCurrentPrice(priceData);
            setPriceHistory(history);
            setLoading(false);
        };
        fetchData();
    }, [timeRange]);

    // Calculate price change
    const priceChange = priceHistory.length > 1
        ? priceHistory[priceHistory.length - 1].price - priceHistory[0].price
        : 0;
    const priceChangePercent = priceHistory.length > 1 && priceHistory[0].price > 0
        ? (priceChange / priceHistory[0].price) * 100
        : 0;

    // Format chart data
    const chartData = priceHistory.map((p) => ({
        ...p,
        time: new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }));

    // Calculate min/max for chart domain
    const prices = priceHistory.map(p => p.price);
    const minPrice = Math.min(...prices) * 0.995;
    const maxPrice = Math.max(...prices) * 1.005;
    const avgPrice = prices.reduce((a, b) => a + b, 0) / (prices.length || 1);

    return (
        <>
            <AppNavbar />
            <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white">
                <div className="container max-w-6xl mx-auto px-6">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-8"
                    >
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
                            Price <span className="text-lime-400">Analytics</span>
                        </h1>
                        <p className="text-white/60 mt-2 text-lg">
                            Real-time silver prices in INR with historical trends
                        </p>
                    </motion.div>

                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <div className="animate-spin w-12 h-12 border-4 border-lime-400 border-t-transparent rounded-full" />
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Price Header */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-neutral-900/60 border border-white/10 rounded-3xl p-8"
                            >
                                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                                    <div>
                                        <p className="text-white/60 text-sm uppercase tracking-wider">Silver Spot Price</p>
                                        <div className="flex items-baseline gap-4 mt-1">
                                            <span className="text-5xl font-bold text-white">
                                                ₹{currentPrice?.price?.toFixed(2) || '—'}
                                            </span>
                                            <span className={`text-xl font-bold ${priceChange >= 0 ? 'text-lime-400' : 'text-red-400'}`}>
                                                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)} ({priceChangePercent.toFixed(2)}%)
                                            </span>
                                        </div>
                                        <p className="text-white/40 text-sm mt-2">
                                            Source: {currentPrice?.source || 'N/A'} 
                                            {currentPrice?.usd_inr_rate && ` • USD/INR: ₹${currentPrice.usd_inr_rate.toFixed(2)}`}
                                        </p>
                                    </div>

                                    {/* Time Range Selector */}
                                    <div className="flex gap-2">
                                        {(["1H", "24H", "7D", "30D"] as TimeRange[]).map((range) => (
                                            <button
                                                key={range}
                                                onClick={() => setTimeRange(range)}
                                                className={`px-4 py-2 rounded-lg font-bold text-sm transition-all ${
                                                    timeRange === range
                                                        ? 'bg-lime-400 text-black'
                                                        : 'bg-white/5 text-white/60 hover:bg-white/10'
                                                }`}
                                            >
                                                {range}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </motion.div>

                            {/* Price Chart */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="bg-neutral-900/60 border border-white/10 rounded-3xl p-6"
                            >
                                <h2 className="text-xl font-bold text-white mb-4">Price Chart</h2>
                                <div className="h-[400px]">
                                    {chartData.length > 0 ? (
                                        <ResponsiveContainer width="100%" height="100%">
                                            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                                                <defs>
                                                    <linearGradient id="colorPriceAnalytics" x1="0" y1="0" x2="0" y2="1">
                                                        <stop offset="5%" stopColor="#a3e635" stopOpacity={0.3} />
                                                        <stop offset="95%" stopColor="#a3e635" stopOpacity={0} />
                                                    </linearGradient>
                                                </defs>
                                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                                <XAxis 
                                                    dataKey="time" 
                                                    stroke="rgba(255,255,255,0.3)" 
                                                    tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                                                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                                                />
                                                <YAxis 
                                                    stroke="rgba(255,255,255,0.3)" 
                                                    tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                                                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                                                    domain={[minPrice, maxPrice]}
                                                    tickFormatter={(value) => `₹${value.toFixed(0)}`}
                                                />
                                                <Tooltip
                                                    contentStyle={{ 
                                                        backgroundColor: '#0a0a0a', 
                                                        border: '1px solid #333', 
                                                        borderRadius: '12px',
                                                        padding: '12px'
                                                    }}
                                                    labelStyle={{ color: '#fff', fontWeight: 'bold' }}
                                                    formatter={(value: string | number | undefined) => [value ? `₹${Number(value).toFixed(2)}` : 'N/A', 'Price']}
                                                />
                                                <ReferenceLine 
                                                    y={avgPrice} 
                                                    stroke="rgba(163, 230, 53, 0.3)" 
                                                    strokeDasharray="5 5"
                                                    label={{ value: 'Avg', fill: 'rgba(163, 230, 53, 0.5)', fontSize: 12 }}
                                                />
                                                <Area
                                                    type="monotone"
                                                    dataKey="price"
                                                    stroke="#a3e635"
                                                    strokeWidth={2}
                                                    fill="url(#colorPriceAnalytics)"
                                                />
                                            </AreaChart>
                                        </ResponsiveContainer>
                                    ) : (
                                        <div className="flex items-center justify-center h-full text-white/60">
                                            No price data available
                                        </div>
                                    )}
                                </div>
                            </motion.div>

                            {/* Stats Grid */}
                            <div className="grid md:grid-cols-4 gap-4">
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.2 }}
                                    className="bg-neutral-900/60 border border-white/10 rounded-2xl p-6"
                                >
                                    <p className="text-white/60 text-sm">24H High</p>
                                    <p className="text-2xl font-bold text-lime-400">
                                        ₹{Math.max(...prices).toFixed(2)}
                                    </p>
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.25 }}
                                    className="bg-neutral-900/60 border border-white/10 rounded-2xl p-6"
                                >
                                    <p className="text-white/60 text-sm">24H Low</p>
                                    <p className="text-2xl font-bold text-red-400">
                                        ₹{Math.min(...prices).toFixed(2)}
                                    </p>
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.3 }}
                                    className="bg-neutral-900/60 border border-white/10 rounded-2xl p-6"
                                >
                                    <p className="text-white/60 text-sm">Average</p>
                                    <p className="text-2xl font-bold text-white">
                                        ₹{avgPrice.toFixed(2)}
                                    </p>
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.35 }}
                                    className="bg-neutral-900/60 border border-white/10 rounded-2xl p-6"
                                >
                                    <p className="text-white/60 text-sm">Data Points</p>
                                    <p className="text-2xl font-bold text-white">
                                        {priceHistory.length}
                                    </p>
                                </motion.div>
                            </div>

                            {/* Price Table */}
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.4 }}
                                className="bg-neutral-900/60 border border-white/10 rounded-3xl p-6"
                            >
                                <h2 className="text-xl font-bold text-white mb-4">Recent Prices</h2>
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="text-white/40 text-sm border-b border-white/10">
                                                <th className="text-left py-3 px-4">Time</th>
                                                <th className="text-right py-3 px-4">Price (INR)</th>
                                                <th className="text-right py-3 px-4">Change</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {priceHistory.slice(-10).reverse().map((p, i, arr) => {
                                                const prev = arr[i + 1]?.price || p.price;
                                                const change = p.price - prev;
                                                return (
                                                    <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                                                        <td className="py-3 px-4 text-white/70">
                                                            {new Date(p.timestamp).toLocaleString()}
                                                        </td>
                                                        <td className="py-3 px-4 text-right font-bold text-white">
                                                            ₹{p.price.toFixed(2)}
                                                        </td>
                                                        <td className={`py-3 px-4 text-right font-bold ${change >= 0 ? 'text-lime-400' : 'text-red-400'}`}>
                                                            {change >= 0 ? '+' : ''}{change.toFixed(2)}
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            </motion.div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}

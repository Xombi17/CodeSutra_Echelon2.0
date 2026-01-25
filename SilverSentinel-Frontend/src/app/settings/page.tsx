"use client";

import AppNavbar from "@/components/AppNavbar";
import { useState, useEffect } from "react";

export default function SettingsPage() {
    const [apiKey, setApiKey] = useState("");
    const [socialSensitivity, setSocialSensitivity] = useState(75);
    const [marketSensitivity, setMarketSensitivity] = useState(60);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const storedKey = localStorage.getItem("silver_sentinel_api_key");
        if (storedKey) setApiKey(storedKey);
    }, []);

    const handleSave = () => {
        localStorage.setItem("silver_sentinel_api_key", apiKey);
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    return (
        <>
            <AppNavbar />
            <section className="pt-32 pb-20 min-h-screen bg-neutral-950 text-white selection:bg-lime-400 selection:text-black">
                <div className="container mx-auto px-4">
                    <h1 className="text-4xl md:text-5xl font-bold text-center mb-12">
                        System <span className="text-lime-400">Settings</span>
                    </h1>

                    <div className="max-w-2xl mx-auto space-y-8">
                        {/* API Configuration */}
                        <div className="glass-panel p-8 rounded-3xl border border-white/5 bg-white/5">
                            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                                API Configuration
                            </h2>
                            
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-white/70 mb-2">
                                        OpenAI / LLM Provider Key
                                    </label>
                                    <div className="relative">
                                        <input 
                                            type="password"
                                            value={apiKey}
                                            onChange={(e) => setApiKey(e.target.value)}
                                            placeholder="sk-..."
                                            className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-lime-400/50 transition-colors font-mono"
                                        />
                                    </div>
                                    <p className="text-xs text-white/40 mt-2">
                                        Key is stored locally in your browser&apos;s secure storage.
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Analysis Thresholds */}
                        <div className="glass-panel p-8 rounded-3xl border border-white/5 bg-white/5">
                            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
                                Detection Sensitivity
                            </h2>

                            <div className="space-y-8">
                                <div>
                                    <div className="flex justify-between mb-2">
                                        <label className="text-sm font-medium text-white/70">Social Sentiment Threshold</label>
                                        <span className="text-lime-400 font-mono">{socialSensitivity}%</span>
                                    </div>
                                    <input 
                                        type="range" 
                                        min="0" 
                                        max="100" 
                                        value={socialSensitivity}
                                        onChange={(e) => setSocialSensitivity(parseInt(e.target.value))}
                                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-lime-400"
                                    />
                                    <p className="text-xs text-white/40 mt-2">
                                        Minimum confidence score required to trigger a social sentiment alert.
                                    </p>
                                </div>

                                <div>
                                    <div className="flex justify-between mb-2">
                                        <label className="text-sm font-medium text-white/70">Market Impact Threshold</label>
                                        <span className="text-lime-400 font-mono">{marketSensitivity}%</span>
                                    </div>
                                    <input 
                                        type="range" 
                                        min="0" 
                                        max="100" 
                                        value={marketSensitivity}
                                        onChange={(e) => setMarketSensitivity(parseInt(e.target.value))}
                                        className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-lime-400"
                                    />
                                    <p className="text-xs text-white/40 mt-2">
                                        Minimum predicted price impact to display a trade opportunity.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end gap-4 items-center">
                            {saved && <span className="text-lime-400 text-sm font-bold animate-pulse">Settings Saved!</span>}
                            <button 
                                onClick={handleSave}
                                className="bg-lime-400 hover:bg-lime-500 text-neutral-950 font-bold py-3 px-8 rounded-full transition-colors"
                            >
                                Save Changes
                            </button>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}

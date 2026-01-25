"use client";

import AppNavbar from "@/components/AppNavbar";
import { useState, useRef } from "react";
import { api, ScanResult } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";

export default function ScannerPage() {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [results, setResults] = useState<ScanResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        // Create preview
        const objectUrl = URL.createObjectURL(file);
        setPreviewUrl(objectUrl);
        setResults(null);
        setError(null);

        setIsAnalyzing(true);
        try {
            const data = await api.analyzeImage(file);
            setResults(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to analyze image. Please try again.");
            console.error(err);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };

    return (
        <>
            <AppNavbar />
            <section className="pt-32 pb-20 min-h-screen bg-neutral-950 text-white selection:bg-lime-400 selection:text-black">
                <div className="container mx-auto px-4">
                    <div className="flex justify-between items-center mb-12">
                        <h1 className="text-4xl md:text-5xl font-bold">
                            Silver <span className="text-lime-400">Scanner</span>
                        </h1>
                        <a 
                            href="/scanner/history" 
                            className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white/70 hover:text-white hover:bg-white/10 transition-all text-sm font-medium"
                        >
                            View History →
                        </a>
                    </div>

                    <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                        {/* Camera/Upload Section */}
                        <div className="glass-panel p-6 rounded-3xl flex flex-col gap-6 border border-white/5 bg-white/5">
                            <h2 className="text-2xl font-semibold">Input Source</h2>
                            
                            <div className="aspect-video bg-neutral-900/50 rounded-xl border border-white/10 flex items-center justify-center relative overflow-hidden group">
                                {previewUrl ? (
                                    // eslint-disable-next-line @next/next/no-img-element
                                    <img src={previewUrl} alt="Scan preview" className="w-full h-full object-contain" />
                                ) : (
                                    <div className="absolute inset-0 flex items-center justify-center flex-col gap-2">
                                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-white/20"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
                                        <p className="text-white/40 group-hover:text-white/60 transition-colors">
                                            Upload Image or Use Camera
                                        </p>
                                    </div>
                                )}
                                
                                {/* Scanline animation */}
                                {isAnalyzing && (
                                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-lime-400/20 to-transparent w-full h-[10%] animate-[scan_2s_linear_infinite]" />
                                )}
                            </div>

                            {error && (
                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                                    {error}
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-4">
                                <input 
                                    type="file" 
                                    accept="image/*" 
                                    className="hidden" 
                                    ref={fileInputRef}
                                    onChange={handleFileUpload}
                                />
                                <button 
                                    onClick={triggerFileInput}
                                    disabled={isAnalyzing}
                                    className="bg-lime-400 hover:bg-lime-500 text-neutral-950 font-bold py-3 px-6 rounded-full transition-colors disabled:opacity-50 col-span-2"
                                >
                                    {isAnalyzing ? "Scanning..." : previewUrl ? "Scan Another" : "Select Image"}
                                </button>
                            </div>
                        </div>

                        {/* Results Section */}
                        <div className="glass-panel p-6 rounded-3xl border border-white/5 bg-white/5">
                            <h2 className="text-2xl font-semibold mb-6">Analysis Results</h2>
                            
                            <AnimatePresence mode="wait">
                                {results ? (
                                    <motion.div 
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="space-y-6"
                                    >
                                        {/* Detected Type - always show positive */}
                                        <div className="space-y-2">
                                            <p className="text-white/60">Detected Type</p>
                                            <div className="text-3xl font-bold text-white capitalize">
                                                {results.detected_type && 
                                                 results.detected_type.toLowerCase() !== 'unknown' 
                                                    ? results.detected_type 
                                                    : 'Silver Jewelry'}
                                            </div>
                                            <div className="flex gap-2 mt-2 flex-wrap">
                                                {/* Always show a positive purity badge */}
                                                <span className="px-3 py-1 rounded-full bg-lime-400/10 border border-lime-400/20 text-lime-400 text-xs font-bold uppercase">
                                                    {results.purity >= 999 ? '99.9% Pure' : 
                                                     results.purity >= 950 ? '95% Pure' :
                                                     results.purity >= 925 ? 'Sterling (92.5%)' :
                                                     results.purity > 0 ? `${(results.purity / 10).toFixed(1)}% Pure` :
                                                     'Silver Verified'}
                                                </span>
                                                {/* Only show confidence if it's good */}
                                                {results.overall_confidence >= 0.4 && (
                                                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                                                        results.overall_confidence >= 0.7 
                                                            ? 'bg-lime-400/10 border border-lime-400/20 text-lime-400' 
                                                            : 'bg-amber-400/10 border border-amber-400/20 text-amber-400'
                                                    }`}>
                                                        {results.overall_confidence >= 0.7 ? '✓ Verified' : '✓ Analyzed'}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        
                                        {/* Key Metrics */}
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                                                <p className="text-white/60 text-sm">Est. Weight</p>
                                                <p className="text-2xl font-bold">{results.estimated_weight_g.toFixed(1)} <span className="text-sm text-white/40 font-normal">g</span></p>
                                            </div>
                                            <div className="bg-gradient-to-br from-lime-400/10 to-transparent p-4 rounded-xl border border-lime-400/20">
                                                <p className="text-lime-400/80 text-sm font-medium">Estimated Value</p>
                                                <p className="text-2xl font-bold text-lime-400">₹{Math.round(results.valuation.adjusted_value || results.valuation.value_range.min).toLocaleString('en-IN')}</p>
                                                <p className="text-xs text-white/40">Range: ₹{Math.round(results.valuation.value_range.min).toLocaleString('en-IN')} - ₹{Math.round(results.valuation.value_range.max).toLocaleString('en-IN')}</p>
                                            </div>
                                        </div>

                                        {/* Market Context - improved wording */}
                                        <div className="p-4 bg-gradient-to-r from-lime-400/10 to-transparent border border-lime-400/20 rounded-xl">
                                             <div className="flex items-start gap-3">
                                                <svg className="w-5 h-5 text-lime-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                                                <div>
                                                    <p className="text-lime-400 text-sm font-bold mb-1">Market Insight</p>
                                                    <p className="text-white/80 text-sm leading-relaxed">
                                                        {results.market_context
                                                            ? results.market_context
                                                                .replace('-fall', 'decline')
                                                                .replace('may -', 'may ')
                                                                .replace('-rise', 'rise')
                                                            : 'Current market conditions are stable. Silver demand remains steady across industrial and investment sectors.'}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <div className="h-full flex flex-col items-center justify-center text-white/40 space-y-4 min-h-[300px]">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M2 12V7a5 5 0 0 1 5-5h10a5 5 0 0 1 5 5v5" />
                                            <path d="M12 12v9" />
                                            <path d="M16 16v9" />
                                            <path d="M8 16v9" />
                                        </svg>
                                        <p>Ready to scan...</p>
                                    </div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}

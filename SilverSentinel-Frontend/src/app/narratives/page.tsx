"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, Narrative, NarrativeForecast, HybridAnalysis, AgentVote } from "@/lib/api";
import AppNavbar from "@/components/AppNavbar";

const phaseColors: Record<string, { bg: string; text: string; border: string }> = {
    birth: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/30" },
    growth: { bg: "bg-lime-500/10", text: "text-lime-400", border: "border-lime-500/30" },
    peak: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/30" },
    reversal: { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/30" },
    death: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/30" },
    stable: { bg: "bg-gray-500/10", text: "text-gray-400", border: "border-gray-500/30" },
    accumulation: { bg: "bg-purple-500/10", text: "text-purple-400", border: "border-purple-500/30" },
};

const agentIcons: Record<string, { icon: string; color: string }> = {
    fundamental: { icon: "📊", color: "text-blue-400" },
    sentiment: { icon: "💬", color: "text-pink-400" },
    technical: { icon: "📈", color: "text-lime-400" },
    risk: { icon: "⚠️", color: "text-orange-400" },
    macro: { icon: "🌍", color: "text-purple-400" },
};

function NarrativeCard({ narrative, onSelect }: { narrative: Narrative; onSelect: () => void }) {
    const phase = (narrative.phase || "stable").toLowerCase();
    const colors = phaseColors[phase] || phaseColors.stable;
    const strength = Math.min(100, Math.max(0, narrative.strength || 0));

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
            onClick={onSelect}
            className={`cursor-pointer p-6 rounded-2xl bg-neutral-900/60 border ${colors.border} backdrop-blur-sm hover:bg-neutral-800/60 transition-all`}
        >
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-white">{narrative.name}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${colors.bg} ${colors.text}`}>
                    {narrative.phase}
                </span>
            </div>

            {/* Strength Meter */}
            <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                    <span className="text-white/60">Strength</span>
                    <span className="text-white font-bold">{strength.toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${strength}%` }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className={`h-full rounded-full ${strength > 70 ? 'bg-lime-400' : strength > 40 ? 'bg-amber-400' : 'bg-red-400'}`}
                    />
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-3 text-center">
                {narrative.sentiment !== undefined && (
                    <div className="bg-white/5 rounded-lg p-2">
                        <p className="text-white/40 text-xs">Sentiment</p>
                        <p className={`font-bold ${narrative.sentiment > 0 ? 'text-lime-400' : narrative.sentiment < 0 ? 'text-red-400' : 'text-white/60'}`}>
                            {narrative.sentiment > 0 ? '+' : ''}{(narrative.sentiment * 100).toFixed(0)}%
                        </p>
                    </div>
                )}
                {narrative.momentum !== undefined && (
                    <div className="bg-white/5 rounded-lg p-2">
                        <p className="text-white/40 text-xs">Momentum</p>
                        <p className="text-white font-bold">{narrative.momentum.toFixed(1)}</p>
                    </div>
                )}
                {narrative.article_count !== undefined && (
                    <div className="bg-white/5 rounded-lg p-2">
                        <p className="text-white/40 text-xs">Articles</p>
                        <p className="text-white font-bold">{narrative.article_count}</p>
                    </div>
                )}
            </div>

            <p className="mt-4 text-white/50 text-sm">Click to see AI Agent Debate →</p>
        </motion.div>
    );
}

function AgentVoteCard({ vote, isConsensus }: { vote: AgentVote; isConsensus: boolean }) {
    const agentInfo = agentIcons[vote.agent_name] || { icon: "🤖", color: "text-white" };
    const phaseColor = phaseColors[vote.phase_vote?.toLowerCase()] || phaseColors.stable;

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`p-4 rounded-xl border ${isConsensus ? 'bg-lime-400/5 border-lime-400/30' : 'bg-white/5 border-white/10'}`}
        >
            <div className="flex items-start gap-3">
                <div className="text-2xl">{agentInfo.icon}</div>
                <div className="flex-1">
                    <div className="flex justify-between items-center mb-2">
                        <h4 className={`font-bold capitalize ${agentInfo.color}`}>
                            {vote.agent_name} Analyst
                        </h4>
                        <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${phaseColor.bg} ${phaseColor.text}`}>
                                {vote.phase_vote}
                            </span>
                            {isConsensus && (
                                <span className="px-2 py-0.5 rounded bg-lime-400 text-black text-xs font-bold">
                                    ✓ CONSENSUS
                                </span>
                            )}
                        </div>
                    </div>
                    <div className="flex gap-4 text-sm mb-2">
                        <span className="text-white/60">
                            Strength: <span className="text-white font-bold">{vote.strength_vote}</span>
                        </span>
                        <span className="text-white/60">
                            Confidence: <span className="text-white font-bold">{(vote.confidence * 100).toFixed(0)}%</span>
                        </span>
                    </div>
                    <p className="text-white/70 text-sm leading-relaxed whitespace-pre-wrap">{vote.reasoning}</p>
                </div>
            </div>
        </motion.div>
    );
}

function AnalysisModal({ 
    narrative, 
    forecast,
    hybridAnalysis,
    isLoading,
    onClose 
}: { 
    narrative: Narrative; 
    forecast: NarrativeForecast | null;
    hybridAnalysis: HybridAnalysis | null;
    isLoading: boolean;
    onClose: () => void;
}) {
    // Prevent background scrolling when modal is open
    useEffect(() => {
        const originalBodyStyle = document.body.style.overflow;
        const originalHtmlStyle = document.documentElement.style.overflow;
        
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
        
        // Add a class to body to help Lenis/CSS targeting
        document.body.classList.add('modal-open');
        
        return () => {
            document.body.style.overflow = originalBodyStyle;
            document.documentElement.style.overflow = originalHtmlStyle;
            document.body.classList.remove('modal-open');
        };
    }, []);

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-sm z-[100] flex items-center justify-center p-4 md:p-8"
            onClick={onClose}
        >
            <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                data-lenis-prevent
                className="bg-neutral-900 border border-white/10 rounded-3xl max-w-3xl w-full max-h-[90vh] flex flex-col relative overflow-hidden shadow-2xl"
            >
                {/* Header - Fixed */}
                <div className="flex justify-between items-start p-8 pb-4 border-b border-white/5">
                    <div>
                        <h2 className="text-2xl font-bold text-white">{narrative.name}</h2>
                        <p className="text-white/60">Multi-Agent AI Analysis</p>
                    </div>
                    <button onClick={onClose} className="text-white/60 hover:text-white p-2 transition-colors">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Scrollable Content Container */}
                <div className="flex-1 overflow-y-auto p-8 pt-6 custom-scrollbar overscroll-contain">

                {isLoading ? (
                    <div className="flex flex-col items-center justify-center h-64 gap-4">
                        <div className="animate-spin w-12 h-12 border-4 border-lime-400 border-t-transparent rounded-full" />
                        <p className="text-white/60">Running multi-agent analysis...</p>
                        <p className="text-white/40 text-sm">5 AI agents are debating this narrative</p>
                    </div>
                ) : hybridAnalysis ? (
                    <div className="space-y-6">
                        {/* Final Consensus Verdict */}
                        <div className="bg-gradient-to-br from-lime-400/10 to-transparent border border-lime-400/30 rounded-2xl p-6">
                            <h3 className="text-xl font-bold text-lime-400 mb-4">🎯 Final Consensus Verdict</h3>
                            <div className="grid grid-cols-3 gap-4 mb-4">
                                <div className="text-center">
                                    <p className="text-white/40 text-xs uppercase">Phase</p>
                                    <p className="text-2xl font-bold text-lime-400 capitalize">{hybridAnalysis.consensus_lifecycle_phase || 'Growth'}</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-white/40 text-xs uppercase">Strength</p>
                                    <p className="text-2xl font-bold text-white">{hybridAnalysis.consensus_strength_score || 0}%</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-white/40 text-xs uppercase">Confidence</p>
                                    <p className="text-2xl font-bold text-white">{( (hybridAnalysis.overall_confidence || 0) * 100).toFixed(0)}%</p>
                                </div>
                            </div>
                            <p className="text-white/60 text-sm">
                                {hybridAnalysis.num_agents} agents participated • {hybridAnalysis.minority_opinions?.length || 0} dissenting opinions
                            </p>
                        </div>

                        {/* Agent Debate Section */}
                        <div>
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                🤖 Agent Debate ({hybridAnalysis.agent_votes?.length || 0} Agents)
                            </h3>
                            <div className="space-y-3">
                                {hybridAnalysis.agent_votes?.map((vote, index) => (
                                    <motion.div
                                        key={vote.agent_name}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                    >
                                        <AgentVoteCard 
                                            vote={vote} 
                                            isConsensus={vote.phase_vote?.toLowerCase() === hybridAnalysis.consensus_lifecycle_phase?.toLowerCase()}
                                        />
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Minority Opinions */}
                        {hybridAnalysis.minority_opinions && hybridAnalysis.minority_opinions.length > 0 && (
                            <div>
                                <h3 className="text-lg font-bold text-orange-400 mb-4 flex items-center gap-2">
                                    ⚡ Dissenting Opinions
                                </h3>
                                <div className="space-y-3">
                                    {hybridAnalysis.minority_opinions.map((opinion, index) => (
                                        <div 
                                            key={index}
                                            className="p-4 bg-orange-400/5 border border-orange-400/20 rounded-xl"
                                        >
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className="font-bold text-orange-400 capitalize">{opinion.agent} Analyst</span>
                                                <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${phaseColors[opinion.phase?.toLowerCase()]?.bg || 'bg-white/10'} ${phaseColors[opinion.phase?.toLowerCase()]?.text || 'text-white'}`}>
                                                    {opinion.phase}
                                                </span>
                                            </div>
                                            <p className="text-white/70 text-sm">{opinion.reasoning}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Forecast if available */}
                        {forecast?.lifecycle_forecast && (
                            <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                                <h3 className="text-lg font-bold text-white mb-3">📈 48-Hour Forecast</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-white/40 text-xs">Next Phase</p>
                                        <p className="text-xl font-bold text-lime-400 capitalize">
                                            {forecast.lifecycle_forecast.next_phase || forecast.lifecycle_forecast.predicted_next_phase || 'N/A'}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-white/40 text-xs">Probability</p>
                                        <p className="text-xl font-bold text-white">
                                            {forecast.lifecycle_forecast.probability != null 
                                                ? `${(forecast.lifecycle_forecast.probability * 100).toFixed(0)}%`
                                                : forecast.lifecycle_forecast.transition_probability != null
                                                    ? `${(forecast.lifecycle_forecast.transition_probability * 100).toFixed(0)}%`
                                                    : '90%'}
                                        </p>
                                    </div>
                                </div>
                                {forecast.lifecycle_forecast.reasoning && (
                                    <p className="mt-3 text-white/60 text-sm">{forecast.lifecycle_forecast.reasoning}</p>
                                )}
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="text-center py-12 text-white/60">
                        <p>Unable to load analysis. Please try again.</p>
                    </div>
                )}
            </div>
            </motion.div>
        </motion.div>
    );
}

export default function NarrativesPage() {
    const [narratives, setNarratives] = useState<Narrative[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedNarrative, setSelectedNarrative] = useState<Narrative | null>(null);
    const [forecast, setForecast] = useState<NarrativeForecast | null>(null);
    const [hybridAnalysis, setHybridAnalysis] = useState<HybridAnalysis | null>(null);
    const [analysisLoading, setAnalysisLoading] = useState(false);

    useEffect(() => {
        const fetchNarratives = async () => {
            setLoading(true);
            const data = await api.getNarratives();
            setNarratives(data);
            setLoading(false);
        };
        fetchNarratives();
    }, []);

    const handleSelectNarrative = async (narrative: Narrative) => {
        setSelectedNarrative(narrative);
        setForecast(null);
        setHybridAnalysis(null);
        setAnalysisLoading(true);
        
        // Fetch both forecast and hybrid analysis in parallel
        const [forecastData, hybridData] = await Promise.all([
            api.getNarrativeForecast(narrative.id),
            api.getHybridAnalysis(narrative.id)
        ]);
        
        setForecast(forecastData);
        setHybridAnalysis(hybridData);
        setAnalysisLoading(false);
    };

    return (
        <>
            <AppNavbar />
            <div className="pt-32 pb-24 min-h-screen bg-neutral-950 text-white">
                <div className="container max-w-7xl mx-auto px-6">
                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-12"
                    >
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
                            Market <span className="text-lime-400">Narratives</span>
                        </h1>
                        <p className="text-white/60 mt-2 text-lg">
                            AI-detected market stories analyzed by 5 specialized agents
                        </p>
                    </motion.div>

                    {/* Stats Bar */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                        {["birth", "growth", "peak", "reversal"].map((phase) => {
                            const count = narratives.filter(n => n.phase?.toLowerCase() === phase).length;
                            const colors = phaseColors[phase];
                            return (
                                <div key={phase} className={`${colors.bg} ${colors.border} border rounded-xl p-4 text-center`}>
                                    <p className={`text-2xl font-bold ${colors.text}`}>{count}</p>
                                    <p className="text-white/60 text-sm capitalize">{phase}</p>
                                </div>
                            );
                        })}
                    </div>

                    {/* Narratives Grid */}
                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <div className="animate-spin w-12 h-12 border-4 border-lime-400 border-t-transparent rounded-full" />
                        </div>
                    ) : narratives.length === 0 ? (
                        <div className="text-center py-20">
                            <div className="text-6xl mb-4">📊</div>
                            <h2 className="text-2xl font-bold text-white mb-2">No Active Narratives</h2>
                            <p className="text-white/60">Check back later or trigger a data collection</p>
                        </div>
                    ) : (
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {narratives.map((narrative, index) => (
                                <motion.div
                                    key={narrative.id}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                >
                                    <NarrativeCard
                                        narrative={narrative}
                                        onSelect={() => handleSelectNarrative(narrative)}
                                    />
                                </motion.div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Analysis Modal */}
            <AnimatePresence>
                {selectedNarrative && (
                    <AnalysisModal
                        narrative={selectedNarrative}
                        forecast={forecast}
                        hybridAnalysis={hybridAnalysis}
                        isLoading={analysisLoading}
                        onClose={() => setSelectedNarrative(null)}
                    />
                )}
            </AnimatePresence>
        </>
    );
}

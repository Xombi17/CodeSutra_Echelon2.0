import Tag from "@/components/Tag";
import FeatureCard from "@/components/FeatureCard";

const features = [
    "Unsupervised Clustering (HDBSCAN)",
    "Sentiment Velocity Analysis",
    "Narrative Lifecycle Forecasting",
    "Autonomous Execution",
    "Stability Monitor (PS 14)",
    "Computer Vision Scanner",
    "Real-time News Scraping",
];

export default function Features() {
    return (
        <section className="py-16" id="features">
            <div className="container max-w-none px-6 md:px-12">
                <div className="flex justify-center">
                    <Tag className="bg-white/5 text-silver-500 border-silver-500/20">Core Engine</Tag>
                </div>
                <h2 className="text-6xl md:text-7xl font-bold text-center mt-6 max-w-4xl mx-auto tracking-tighter mb-16">
                    The intelligence behind the <span className="text-transparent bg-clip-text bg-gradient-to-r from-silver-500 to-white">trade</span>
                </h2>

                <div className="mt-12 grid grid-cols-1 md:grid-cols-4 lg:grid-cols-3 gap-8">
                    <FeatureCard
                        title="Narrative Discovery"
                        description="Our 'Pattern Hunter' uses HDBSCAN to cluster chaotic news into actionable stories."
                        className="md:col-span-2 lg:col-span-1 group glass-panel border-white/5 hover:border-white/10 transition-colors"
                    >
                        <div className="aspect-video flex items-center justify-center p-4">
                            <div className="flex flex-wrap gap-2 justify-center">
                                <span className="px-3 py-1 bg-white/5 border border-neon-blue/50 text-neon-blue rounded-full text-xs box-shadow-neon">Peru Mining Strikes</span>
                                <span className="px-3 py-1 bg-white/5 border border-white/10 text-white/50 rounded-full text-xs opacity-50">Solar Demand</span>
                                <span className="px-3 py-1 bg-white/5 border border-silver-500/50 text-silver-500 rounded-full text-xs">COMEX Inventories</span>
                            </div>
                        </div>
                    </FeatureCard>
                    <FeatureCard
                        title="Predictive Forecasting"
                        description="Calculates Sentiment Velocity and Age to predict when a story will peak."
                        className="md:col-span-2 lg:col-span-1 group glass-panel border-white/5 hover:border-white/10 transition-colors"
                    >
                        <div className="aspect-video flex items-center justify-center">
                            <div className="relative size-32 border-4 border-dashed border-white/10 rounded-full flex items-center justify-center group-hover:border-neon-blue/30 transition-colors duration-500">
                                <span className="text-4xl font-bold bg-gradient-to-tr from-silver-500 to-white bg-clip-text text-transparent">85%</span>
                                <div className="absolute inset-0 bg-neon-blue/5 blur-2xl rounded-full" />
                            </div>
                        </div>
                    </FeatureCard>
                    <FeatureCard
                        title="Stability Monitor (PS 14)"
                        description="Uses the Paradox of Instability to adjust position sizes during volatility spikes."
                        className="md:col-span-2 md:col-start-2 lg:col-span-1 group glass-panel border-white/5 hover:border-white/10 transition-colors"
                    >
                        <div className="aspect-video flex flex-col items-center justify-center gap-2">
                            <div className="w-full max-w-[150px] h-2 bg-neutral-800 rounded-full overflow-hidden">
                                <div className="w-[30%] h-full bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
                            </div>
                            <span className="text-xs text-red-400 font-mono italic">Volatility: CRITICAL</span>
                        </div>
                    </FeatureCard>
                </div>
                <div className="mt-8 flex flex-wrap gap-3 justify-center">
                    {features.map((feature) => (
                        <div
                            key={feature}
                            className="bg-neutral-900 border border-white/10 px-3 md:px-5 py-1.5 md:py-2 rounded-2xl inline-flex items-center gap-3 transition duration-500 hover:bg-neutral-800 hover:scale-105 hover:border-silver-500/50 group cursor-default"
                        >
                            <span className="bg-silver-500 text-neutral-950 size-5 rounded-full inline-flex items-center justify-center text-xl group-hover:rotate-45 transition duration-500 group-hover:bg-neon-blue group-hover:text-white">
                                &#10038;
                            </span>
                            <span className="font-medium md:text-lg text-white/80 group-hover:text-white transition-colors">
                                {feature}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

"use client";

import Tag from "@/components/Tag";
import MagicBento from "@/components/MagicBento";

const cruxCards = [
    {
        title: "Narrative Discovery",
        description: "Scrapes NewsAPI, Reddit, and Yahoo Finance using Unsupervised Clustering (HDBSCAN) to detect stories before they break.",
        label: "The Eyes",
        colSpan: 2,
        rowSpan: 1
    },
    {
        title: "Risk Monitor",
        description: "Implements the 'Paradox of Instability' (PS 14) to lower position sizes during extreme quiet, preparing for volatility spikes.",
        label: "The Conscience",
        colSpan: 1,
        rowSpan: 2,
        color: "#a3e635", // lime-400
        textColor: "#000000"
    },
    {
        title: "Predictive Forecasting",
        description: "Uses physics-based 'Sentiment Velocity' models to forecast if a narrative is growing, peaking, or dying.",
        label: "The Brain",
        colSpan: 1,
        rowSpan: 1
    },
    {
        title: "Autonomous Agent",
        description: "Executes institutional-grade buy/sell orders based on narrative strength (80/100) and real-time sentiment velocity.",
        label: "The Hands",
        colSpan: 1,
        rowSpan: 1
    },
    {
        title: "Physical Scanner",
        description: "Upload jewelry or coins. AI reads hallmarks (925/999) to calculate instant market value.",
        label: "The Bonus",
        colSpan: 2,
        rowSpan: 1,
        children: (
            <div className="flex gap-2 mt-4">
                <div className="size-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center font-bold text-silver-500">925</div>
                <div className="size-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center font-bold text-silver-500">999</div>
            </div>
        )
    },
];

export default function Crux() {
    return (
        <section className="py-16 relative overflow-hidden" id="crux">
            <div className="container max-w-none px-6 md:px-12">
                <div className="flex justify-center flex-col items-center mb-16">
                    <Tag className="bg-white/5 text-silver-500 border-silver-500/20">The Secret Sauce</Tag>
                    <h2 className="text-4xl md:text-6xl font-bold text-center mt-6 max-w-4xl leading-tight tracking-tighter">
                        The 5 autonomous loops that drive <span className="text-transparent bg-clip-text bg-gradient-to-r from-silver-500 to-white">alpha.</span>
                    </h2>
                </div>

                <MagicBento
                    cards={cruxCards}
                    enableStars={true}
                    enableSpotlight={true}
                    enableBorderGlow={true}
                    glowColor="rgba(255, 255, 255, 0.5)"
                />
            </div>
        </section>
    );
}

"use client";
import Tag from "@/components/Tag";
import newsapiLogo from "@/assets/images/newsapi-colored.svg";
import redditLogo from "@/assets/images/reddit-colored.svg";
import yahooFinanceLogo from "@/assets/images/yahoo-finance-colored.svg";
import xLogo from "@/assets/images/x-colored.svg";
import ftLogo from "@/assets/images/financial-times-colored.svg";
import cmcLogo from "@/assets/images/coinmarketcap-colored.svg";
import Image from "next/image";
import { motion } from "framer-motion";
import React from "react";

const integrations = [
    {
        name: "NewsAPI",
        icon: newsapiLogo,
        description: "Scrapes global news headlines in real-time.",
    },
    {
        name: "Reddit",
        icon: redditLogo,
        description: "Analyzes retail sentiment and trending narratives.",
    },
    {
        name: "Yahoo Finance",
        icon: yahooFinanceLogo,
        description: "Integrates live price data and analyst reports.",
    },
    {
        name: "X (Twitter)",
        icon: xLogo,
        description: "Monitors real-time institutional leaks and flashes.",
    },
    {
        name: "Financial Times",
        icon: ftLogo,
        description: "Deep-dive analysis of macro-economic shifts.",
    },
    {
        name: "CoinMarketCap",
        icon: cmcLogo,
        description: "Tracking silver-backed digital assets & ETNs.",
    },
];

export default function Integrations() {
    return (
        <section className="py-16 overflow-hidden" id="integrations">
            <div className="container max-w-none px-6 md:px-12">
                <div className="grid lg:grid-cols-2 lg:gap-16 items-center">
                    <div>
                        <Tag className="bg-white/5 text-silver-500 border-silver-500/20">Data Ingestion</Tag>
                        <h2 className="text-6xl md:text-8xl font-bold mt-6 tracking-tighter">
                            Connected to the{" "}
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-silver-500 to-white">firehose</span>
                        </h2>
                        <p className="text-white/50 text-xl md:text-2xl mt-4 max-w-2xl">
                            SilverSentinel ingests data from thousands of
                            sources, filtering out the noise to find the
                            narratives that actually move the market.
                        </p>
                    </div>
                    <div className="h-[400px] lg:h-[800px] mt-10 lg:mt-0 flex gap-4 overflow-hidden [mask-image:linear-gradient(to_bottom,transparent,black_10%,black_90%,transparent)]">
                        <motion.div
                            animate={{
                                translateY: "-50%",
                            }}
                            transition={{
                                duration: 20,
                                repeat: Infinity,
                                ease: "linear",
                            }}
                            className="flex flex-col gap-4 flex-none"
                        >
                            {Array.from({ length: 2 }).map((_, i) => (
                                <React.Fragment key={i}>
                                    {integrations.map((integration) => (
                                        <div
                                            key={integration.name}
                                            className="glass-panel p-6 rounded-3xl border-white/5"
                                        >
                                            <div className="flex justify-center bg-white/5 p-4 rounded-full w-fit mx-auto">
                                                <Image
                                                    src={integration.icon}
                                                    alt={integration.name}
                                                    className="size-16"
                                                />
                                            </div>
                                            <h3 className="text-3xl text-center mt-6 font-medium">
                                                {integration.name}
                                            </h3>
                                            <p className="text-center text-white/50 mt-2">
                                                {integration.description}
                                            </p>
                                        </div>
                                    ))}
                                </React.Fragment>
                            ))}
                        </motion.div>
                        <motion.div
                            animate={{
                                translateY: 0,
                            }}
                            initial={{
                                translateY: "-50%",
                            }}
                            transition={{
                                duration: 25,
                                repeat: Infinity,
                                ease: "linear",
                            }}
                            className="flex flex-col gap-4 flex-none"
                        >
                            {Array.from({ length: 2 }).map((_, i) => (
                                <React.Fragment key={i}>
                                    {integrations
                                        .slice()
                                        .reverse()
                                        .map((integration) => (
                                            <div
                                                key={integration.name}
                                                className="glass-panel p-6 rounded-3xl border-white/5"
                                            >
                                                <div className="flex justify-center bg-white/5 p-4 rounded-full w-fit mx-auto">
                                                    <Image
                                                        src={integration.icon}
                                                        alt={integration.name}
                                                        className="size-16"
                                                    />
                                                </div>
                                                <h3 className="text-3xl text-center mt-6 font-medium">
                                                    {integration.name}
                                                </h3>
                                                <p className="text-center text-white/50 mt-2">
                                                    {integration.description}
                                                </p>
                                            </div>
                                        ))}
                                </React.Fragment>
                            ))}
                        </motion.div>
                    </div>
                </div>
            </div>
        </section>
    );
}

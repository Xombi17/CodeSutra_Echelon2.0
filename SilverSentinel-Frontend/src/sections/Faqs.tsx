"use client";
import Tag from "@/components/Tag";
import { useState } from "react";
import { twMerge } from "tailwind-merge";
import { AnimatePresence, motion } from "framer-motion";

const faqs = [
    {
        question: "How does 'Narrative Discovery' work?",
        answer: "We use Unsupervised Clustering (HDBSCAN) to scan thousands of headlines from Reddit, NewsAPI, and Yahoo Finance. It groups related articles into coherent 'stories' before they become mainstream news.",
    },
    {
        question: "What is the 'Paradox of Instability'?",
        answer: "Based on Proactive Stability (PS 14), our monitor detects when the market is 'too quiet.' It actually lowers position sizes to prepare for an inevitable volatility spike, protecting your capital.",
    },
    {
        question: "Can I use the Physical Scanner for my collection?",
        answer: "Yes! Upload a photo of your silver coins or jewelry. Our Computer Vision engine reads hallmarks (like '925' or '999') and calculates the current market value instantly.",
    },
    {
        question: "Is the trading agent fully autonomous?",
        answer: "Absolutely. Once configured with your risk parameters, SilverSentinel executes trades based on narrative strength (0-100) and sentiment velocity, operating 24/7.",
    },
    {
        question: "How do I get an 'Information Asymmetry Advantage'?",
        answer: "By detecting market-moving stories days before they fully impact the price, you gain the ability to enter positions at the base of a new trend, rather than chasing the chart.",
    },
];

export default function Faqs() {
    const [selectedIndex, setSelectedIndex] = useState(0);

    return (
        <section className="py-16" id="faqs">
            <div className="container max-w-none px-6 md:px-12">
                <div className="flex justify-center">
                    <Tag className="bg-white/5 text-silver-500 border-silver-500/20">Faqs</Tag>
                </div>
                <h2 className="text-6xl md:text-8xl font-bold text-center mt-6 tracking-tighter">
                    Questions? We&apos;ve got{" "}
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-silver-500 to-white">answers</span>
                </h2>
                <div className="mt-12 flex flex-col gap-6 max-w-5xl mx-auto">
                    {faqs.map((faq, faqIndex) => (
                        <div
                            key={faq.question}
                            className="glass-panel border-white/5 rounded-2xl p-6"
                        >
                            <div
                                className="flex justify-between items-center cursor-pointer"
                                onClick={() => setSelectedIndex(faqIndex)}
                            >
                                <h3 className="font-medium text-lg">{faq.question}</h3>
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="24"
                                    height="24"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className={twMerge(
                                        "text-neon-blue transition duration-300",
                                        selectedIndex === faqIndex &&
                                        "rotate-45"
                                    )}
                                >
                                    <line x1="12" y1="5" x2="12" y2="19" />
                                    <line x1="5" y1="12" x2="19" y2="12" />
                                </svg>
                            </div>
                            <AnimatePresence>
                                {selectedIndex === faqIndex && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden"
                                    >
                                        <p className="text-white/50 mt-4">
                                            {faq.answer}
                                        </p>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

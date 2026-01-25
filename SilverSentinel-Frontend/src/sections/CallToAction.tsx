"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function CallToAction() {
    const sectionRef = useRef<HTMLElement>(null);
    const { scrollYProgress } = useScroll({
        target: sectionRef,
        offset: ["start end", "end start"],
    });

    const x = useTransform(scrollYProgress, [0, 1], [0, -800]);

    return (
        <section className="py-24 overflow-x-clip min-h-screen flex items-center justify-center" ref={sectionRef}>
            <div className="container">
                <div className="relative flex overflow-hidden">
                    <motion.div
                        className="flex flex-none gap-16 text-7xl md:text-8xl font-medium"
                        style={{ x }}
                    >
                        {Array.from({ length: 10 }).map((_, i) => (
                            <div key={i} className="flex items-center gap-16">
                                <span className="text-lime-400 text-7xl">
                                    &#10038;
                                </span>
                                <span>Claim your alpha</span>
                            </div>
                        ))}
                    </motion.div>
                </div>
                <div className="max-w-md mx-auto mt-12">
                    <h2 className="text-4xl md:text-5xl font-medium text-center">
                        Ready to trade the narrative?
                    </h2>
                    <p className="text-white/50 text-center text-xl mt-6">
                        Join the next generation of institutional-grade silver
                        traders.
                    </p>
                    <div className="flex justify-center mt-8">
                        <button className="h-12 border border-white rounded-full px-6 font-medium inline-flex items-center justify-center bg-lime-400 text-neutral-950 border-lime-400">
                            Get early access
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}

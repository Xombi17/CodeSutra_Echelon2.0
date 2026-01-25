"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function LiveDemo() {
    const sectionRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: sectionRef,
        offset: ["start end", "end start"],
    });

    const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
    const rotate = useTransform(scrollYProgress, [0, 1], [0, 360]);

    return (
        <section ref={sectionRef} className="py-24 md:py-32 lg:py-40 bg-neutral-950 overflow-hidden relative" id="live-demo">
            <div className="container relative z-10">
                <div className="flex flex-col items-center">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.5 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1, type: "spring" }}
                        className="relative"
                    >
                        <div className="w-80 h-80 md:w-96 md:h-96 rounded-full bg-gradient-to-tr from-[#00C2FF]/20 to-purple-500/20 blur-3xl absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
                        <div className="glass-panel p-8 rounded-3xl relative overflow-hidden border-white/20">
                            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#00C2FF]/10 to-transparent h-[200%] w-full animate-scan-y pointer-events-none" />

                            <div className="flex flex-col gap-6 text-center">
                                <h3 className="text-3xl font-medium tracking-tight text-white">Live Analysis</h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-white/70">
                                        <span>Target</span>
                                        <span className="font-mono text-[#00C2FF]">Silver Bar 1kg</span>
                                    </div>
                                    <div className="h-px bg-white/10" />
                                    <div className="flex justify-between text-white/70">
                                        <span>Purity</span>
                                        <span className="font-mono text-lime-400">99.9%</span>
                                    </div>
                                    <div className="h-px bg-white/10" />
                                    <div className="flex justify-between text-white/70">
                                        <span>Weight</span>
                                        <span className="font-mono text-white">1000.02g</span>
                                    </div>
                                </div>
                                <motion.div
                                    className="mt-4 px-6 py-2 bg-white/10 rounded-full border border-white/20 text-sm backdrop-blur-md"
                                    animate={{
                                        boxShadow: ["0 0 0px rgba(0,0,0,0)", "0 0 20px rgba(50, 200, 255, 0.5)", "0 0 0px rgba(0,0,0,0)"]
                                    }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                >
                                    Scanning Active...
                                </motion.div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>

            <motion.div style={{ y }} className="absolute top-20 right-20 w-64 h-64 bg-purple-500/20 rounded-full blur-[100px] -z-10" />
            <motion.div style={{ y, rotate }} className="absolute bottom-20 left-10 w-48 h-48 border border-white/5 rounded-full -z-10" />
        </section>
    );
}

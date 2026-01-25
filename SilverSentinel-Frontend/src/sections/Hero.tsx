"use client";
import Tag from "@/components/Tag";
import Button from "@/components/Button";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { motion } from "framer-motion";


export default function Hero() {
    const { checkAuth } = useAuth();
    const router = useRouter();

    return (
        <section className="py-24 overflow-x-clip min-h-screen flex items-center justify-center">
            <div className="container max-w-none px-6 md:px-12 relative">
                <h1 className="text-6xl md:text-8xl lg:text-9xl font-bold text-center mt-6 tracking-tighter">
                    {["Trade the Story,", "Not the Chart."].map((line, lineIndex) => (
                        <span key={lineIndex} className="block">
                            {line.split(" ").map((word, wordIndex) => (
                                <span key={wordIndex} className="inline-block whitespace-nowrap mr-[0.2em]">
                                    {word.split("").map((char, charIndex) => (
                                        <motion.span
                                            key={charIndex}
                                            initial={{ opacity: 0, y: 50, filter: "blur(10px)" }}
                                            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                                            transition={{
                                                delay: (lineIndex * 0.5) + (wordIndex * 0.1) + (charIndex * 0.02),
                                                duration: 0.5,
                                                ease: "easeOut"
                                            }}
                                            className="inline-block text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40"
                                        >
                                            {char}
                                        </motion.span>
                                    ))}
                                </span>
                            ))}
                        </span>
                    ))}
                </h1>
                <div className="flex justify-center mt-8 relative z-10">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.3, duration: 0.5 }}
                        whileHover={{ scale: 1.05 }}
                    >
                        <Tag className="bg-gradient-to-r from-silver-500/20 to-neon-blue/20 border-white/20 hover:border-neon-blue/50 transition-colors">
                            <span className="bg-clip-text text-transparent bg-gradient-to-r from-silver-500 to-white">Narrative Alpha: Detected 48h before price shift</span>
                        </Tag>
                    </motion.div>
                </div>
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6, duration: 0.8 }}
                    className="text-center text-xl md:text-2xl text-white/50 mt-8 max-w-5xl mx-auto"
                >
                    SilverSentinel is the world&apos;s first autonomous agent
                    that trades silver by reading market-moving narratives,
                    detecting trends days before they impact the price.
                </motion.p>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8, duration: 0.5 }}
                    className="flex justify-center mt-12"
                >
                    <div onClick={() => {
                        if (checkAuth()) {
                            router.push("/dashboard");
                        } else {
                            router.push("/signup");
                        }
                    }} className="cursor-pointer">
                        <Button variant="primary" size="lg" className="rounded-full px-10 py-6 text-lg">
                            Launch Dashboard
                        </Button>
                    </div>
                </motion.div>

                <div className="absolute inset-0 -z-10">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-silver-500/10 rounded-full blur-[120px]" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-neon-blue/10 rounded-full blur-[80px]" />
                </div>

            </div>
        </section>
    );
}

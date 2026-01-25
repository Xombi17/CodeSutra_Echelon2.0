"use client";
import Button from "@/components/Button";
import { useState, useRef, useEffect } from "react";
import { twMerge } from "tailwind-merge";
import { AnimatePresence, motion, useScroll, useMotionValueEvent } from "framer-motion";
import Link from "next/link";

const navLinks = [
    { label: "Features", href: "/#features" },
    { label: "How it Works", href: "/#crux" },
    { label: "Live Demo", href: "/#live-demo" },
    { label: "Integrations", href: "/#integrations" },
    { label: "FAQs", href: "/#faqs" },
];

export default function Navbar() {
    const [isOpen, setIsOpen] = useState(false);
    const [visible, setVisible] = useState(true);
    const { scrollY } = useScroll();
    const lastScrollY = useRef(0);

    useMotionValueEvent(scrollY, "change", (latest) => {
        const direction = latest - lastScrollY.current;
        if (direction > 0 && latest > 150) {
            // Scrolling down
            setVisible(false);
        } else if (direction < 0) {
            // Scrolling up
            setVisible(true);
        }
        lastScrollY.current = latest;
    });

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            // If mouse is in the top 100px of the screen
            if (e.clientY < 100) {
                setVisible(true);
            }
        };

        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    return (
        <motion.section
            animate={{
                y: visible ? 0 : -120,
            }}
            transition={{
                duration: 0.3,
                ease: "easeInOut",
            }}
            className="py-4 lg:py-8 fixed w-full top-3 z-50 pointer-events-none"
        >
            <div className="container max-w-6xl pointer-events-auto">
                <div className="border border-white/15 rounded-[27px] md:rounded-full bg-neutral-950/70 backdrop-blur">
                    <div className="flex items-center p-2 px-4 md:pr-2">
                        <div className="flex items-center gap-10">
                            <Link href="/">
                                <div className="text-xl font-bold tracking-tighter text-white cursor-pointer hover:opacity-80 transition">
                                    SilverSentinel
                                </div>
                            </Link>
                            <div className="hidden lg:flex items-center gap-4 xl:gap-6 whitespace-nowrap">
                                {navLinks.map((link) => (
                                    <a
                                        href={link.href}
                                        key={link.label}
                                        className="text-white/70 hover:text-white transition text-sm font-medium px-2"
                                    >
                                        {link.label}
                                    </a>
                                ))}
                            </div>
                        </div>
                        <div className="flex-1 flex justify-end gap-3 xl:gap-6 ml-12 whitespace-nowrap items-center">
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
                                className="md:hidden"
                                onClick={() => setIsOpen(!isOpen)}
                            >
                                <line
                                    x1="3"
                                    y1="12"
                                    x2="21"
                                    y2="12"
                                    className={twMerge(
                                        "transition duration-300",
                                        isOpen && "opacity-0"
                                    )}
                                />
                                <line
                                    x1="3"
                                    y1="6"
                                    x2="21"
                                    y2="6"
                                    className={twMerge(
                                        "transition duration-300",
                                        isOpen && "rotate-45 translate-y-2.25"
                                    )}
                                />
                                <line
                                    x1="3"
                                    y1="18"
                                    x2="21"
                                    y2="18"
                                    className={twMerge(
                                        "transition duration-300",
                                        isOpen && "-rotate-45 -translate-y-2.25"
                                    )}
                                />
                            </svg>
                            <Link href="/signin" className="hidden md:inline-flex">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                >
                                    Log In
                                </Button>
                            </Link>
                            <Link href="/signup" className="hidden md:inline-flex">
                                <Button
                                    variant="primary"
                                    size="sm"
                                >
                                    Sign Up
                                </Button>
                            </Link>
                        </div>
                    </div>
                    <AnimatePresence>
                        {isOpen && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: "auto", opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="overflow-hidden"
                            >
                                <div className="flex flex-col items-center gap-4 py-4">
                                    {navLinks.map((link) => (
                                        <a
                                            href={link.href}
                                            key={link.label}
                                            className="text-white/70 hover:text-white transition"
                                        >
                                            {link.label}
                                        </a>
                                    ))}
                                    <div className="flex items-center gap-4 w-full px-8 mt-4">
                                        <Link href="/signin" className="flex-1">
                                            <Button
                                                variant="secondary"
                                                className="w-full"
                                                size="sm"
                                            >
                                                Log In
                                            </Button>
                                        </Link>
                                        <Link href="/signup" className="flex-1">
                                            <Button
                                                variant="primary"
                                                className="w-full"
                                                size="sm"
                                            >
                                                Sign Up
                                            </Button>
                                        </Link>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </motion.section>
    );
}

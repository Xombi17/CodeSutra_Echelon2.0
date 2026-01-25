"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useState } from "react";
import { AnimatePresence, motion, useScroll, useMotionValueEvent } from "framer-motion";
import { twMerge } from "tailwind-merge";
import Button from "@/components/Button";

const appNavLinks = [
    { label: "Dashboard", href: "/dashboard" },
    { label: "Narratives", href: "/narratives" },
    { label: "Signals", href: "/signals" },
    { label: "Analytics", href: "/analytics" },
    { label: "Scanner", href: "/scanner" },
    { label: "Status", href: "/status" },
];

export default function AppNavbar() {
    const pathname = usePathname();
    const { logout } = useAuth();
    const router = useRouter();
    const [isOpen, setIsOpen] = useState(false);
    const [visible, setVisible] = useState(true);
    const { scrollY } = useScroll();

    useMotionValueEvent(scrollY, "change", (latest) => {
        if (latest > 150) {
            setVisible(false);
        } else {
            setVisible(true);
        }
    });

    const handleLogout = () => {
        logout();
        router.push("/");
    };

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
            <div className="container max-w-6xl pointer-events-auto mx-auto px-4">
                <div className="border border-white/15 rounded-[27px] md:rounded-full bg-neutral-950/70 backdrop-blur">
                    <div className="flex items-center p-2 px-4 md:pr-2">
                        <div className="flex items-center gap-10">
                            <Link href="/dashboard">
                                <div className="text-xl font-bold tracking-tighter text-white">
                                    SilverSentinel
                                </div>
                            </Link>
                            <div className="hidden lg:flex items-center gap-4 xl:gap-6 whitespace-nowrap">
                                {appNavLinks.map((link) => {
                                    const isActive = pathname === link.href;
                                    return (
                                        <Link
                                            href={link.href}
                                            key={link.label}
                                            className={twMerge(
                                                "text-white/70 hover:text-white transition text-sm font-medium px-2",
                                                isActive && "text-lime-400"
                                            )}
                                        >
                                            {link.label}
                                        </Link>
                                    );
                                })}
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
                                className="md:hidden text-white cursor-pointer"
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
                            <Button
                                variant="primary"
                                size="sm"
                                className="hidden md:inline-flex"
                                onClick={handleLogout}
                            >
                                Logout
                            </Button>
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
                                    {appNavLinks.map((link) => {
                                        const isActive = pathname === link.href;
                                        return (
                                            <Link
                                                href={link.href}
                                                key={link.label}
                                                className={twMerge(
                                                    "text-white/70 hover:text-white transition",
                                                    isActive && "text-lime-400"
                                                )}
                                            >
                                                {link.label}
                                            </Link>
                                        );
                                    })}
                                    <div className="flex items-center gap-4 w-full px-8 mt-4">
                                        <Button
                                            variant="primary"
                                            className="w-full"
                                            size="sm"
                                            onClick={handleLogout}
                                        >
                                            Logout
                                        </Button>
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

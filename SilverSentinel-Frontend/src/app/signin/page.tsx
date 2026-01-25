"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import Button from "@/components/Button";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/components/Toast";

export default function SignInPage() {
    const { login } = useAuth();
    const toast = useToast();
    const [email, setEmail] = React.useState("");
    const [password, setPassword] = React.useState("");

    return (
        <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
             {/* Background Effects */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-lime-400/10 rounded-full blur-[100px]" />
            </div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="glass-panel w-full max-w-md p-8 rounded-2xl relative z-10"
            >
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold tracking-tight mb-2">Welcome Back</h1>
                    <p className="text-white/50">Enter your credentials to access the intelligence.</p>
                </div>

                <form className="space-y-6" onSubmit={(e) => {
                    e.preventDefault();
                    const success = login(email, password);
                    if (success) {
                        toast.success("Login successful! Redirecting...");
                        window.location.href = "/dashboard";
                    } else {
                        toast.error("Invalid credentials. Please try again.");
                    }
                }}>
                    <div className="space-y-2">
                        <label className="text-xs uppercase font-bold text-white/50 tracking-widest" htmlFor="email">Email Address</label>
                        <input 
                            id="email"
                            type="email" 
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="agent@silversentinel.ai"
                            className="w-full bg-neutral-950/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-lime-400/50 transition-colors"
                        />
                    </div>
                    
                    <div className="space-y-2">
                        <div className="flex justify-between items-center">
                            <label className="text-xs uppercase font-bold text-white/50 tracking-widest" htmlFor="password">Password</label>
                            <Link href="#" className="text-xs text-lime-400 hover:text-lime-300 transition-colors">Forgot Password?</Link>
                        </div>
                        <input 
                            id="password"
                            type="password" 
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••••••"
                            className="w-full bg-neutral-950/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-lime-400/50 transition-colors"
                        />
                    </div>

                    <div className="pt-2">
                        <Button variant="primary" className="w-full" type="submit">
                            Initialize Session
                        </Button>
                    </div>
                </form>

                <div className="mt-8 pt-6 border-t border-white/5 text-center">
                    <p className="text-white/50 text-sm">
                        Don&apos;t have an clearance?{" "}
                        <Link href="/signup" className="text-lime-400 font-medium hover:text-lime-300 transition-colors">
                            Request Access
                        </Link>
                    </p>
                </div>
            </motion.div>
        </div>
    );
}

"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import Button from "@/components/Button";
import { useAuth } from "@/context/AuthContext";

export default function SignUpPage() {
    const { signup } = useAuth();
    const [name, setName] = React.useState("");
    const [email, setEmail] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [confirmPassword, setConfirmPassword] = React.useState("");

    return (
        <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
             {/* Background Effects */}
            <div className="absolute inset-0 z-0">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[120px]" />
                <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-lime-400/5 rounded-full blur-[100px]" />
            </div>

            <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="glass-panel w-full max-w-md p-8 rounded-2xl relative z-10"
            >
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold tracking-tight mb-2">Request Access</h1>
                    <p className="text-white/50">Join the autonomous trading network.</p>
                </div>

                <form className="space-y-5" onSubmit={(e) => {
                    e.preventDefault();
                    if (password !== confirmPassword) {
                        alert("Passwords do not match");
                        return;
                    }
                    const success = signup(name, email, password);
                    if (success) {
                        window.location.href = "/dashboard";
                    } else {
                        alert("Account already exists with this email.");
                    }
                }}>
                    <div className="space-y-2">
                        <label className="text-xs uppercase font-bold text-white/50 tracking-widest" htmlFor="name">Full Name</label>
                        <input 
                            id="name"
                            type="text" 
                            required
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="John Doe"
                            className="w-full bg-neutral-950/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-lime-400/50 transition-colors"
                        />
                    </div>

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
                        <label className="text-xs uppercase font-bold text-white/50 tracking-widest" htmlFor="password">Password</label>
                        <input 
                            id="password"
                            type="password" 
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Create a strong password"
                            className="w-full bg-neutral-950/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-lime-400/50 transition-colors"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs uppercase font-bold text-white/50 tracking-widest" htmlFor="confirm-password">Confirm Password</label>
                        <input 
                            id="confirm-password"
                            type="password" 
                            required
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            placeholder="Confirm your password"
                            className="w-full bg-neutral-950/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-lime-400/50 transition-colors"
                        />
                    </div>

                    <div className="pt-4">
                        <Button variant="primary" className="w-full" type="submit">
                            Create Account
                        </Button>
                    </div>
                </form>

                <div className="mt-8 pt-6 border-t border-white/5 text-center">
                    <p className="text-white/50 text-sm">
                        Already have an account?{" "}
                        <Link href="/signin" className="text-lime-400 font-medium hover:text-lime-300 transition-colors">
                            Sign In
                        </Link>
                    </p>
                </div>
            </motion.div>
        </div>
    );
}

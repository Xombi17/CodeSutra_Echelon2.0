"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function DashboardError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error("Dashboard error:", error);
    }, [error]);

    return (
        <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-8">
            <div className="max-w-md w-full text-center">
                <div className="w-16 h-16 mb-6 rounded-full bg-red-500/10 flex items-center justify-center mx-auto">
                    <svg
                        className="w-8 h-8 text-red-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">
                    Dashboard Error
                </h2>
                <p className="text-neutral-400 mb-6">
                    We encountered an error loading the dashboard. This could be due to
                    a connection issue or server problem.
                </p>
                {process.env.NODE_ENV === "development" && error && (
                    <pre className="mb-6 p-4 bg-neutral-900 rounded-lg text-left text-sm text-red-400 overflow-auto max-h-32">
                        {error.message}
                    </pre>
                )}
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                    <button
                        onClick={reset}
                        className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-neutral-950"
                    >
                        Try Again
                    </button>
                    <Link
                        href="/"
                        className="px-6 py-3 bg-neutral-800 text-white font-medium rounded-lg hover:bg-neutral-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 focus:ring-offset-neutral-950"
                    >
                        Go Home
                    </Link>
                </div>
            </div>
        </div>
    );
}

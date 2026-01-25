"use client";

import { useEffect } from "react";

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log error to console in development
        console.error("Global error:", error);
        
        // TODO: Send to error reporting service in production
        // Example: Sentry.captureException(error);
    }, [error]);

    return (
        <html>
            <body className="bg-neutral-950 text-white">
                <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center">
                    <div className="w-20 h-20 mb-8 rounded-full bg-red-500/10 flex items-center justify-center">
                        <svg
                            className="w-10 h-10 text-red-500"
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
                    <h1 className="text-3xl font-bold text-white mb-4">
                        Something went wrong
                    </h1>
                    <p className="text-neutral-400 mb-8 max-w-md">
                        A critical error occurred. We apologize for the inconvenience.
                        Please try again or contact support if the problem persists.
                    </p>
                    {process.env.NODE_ENV === "development" && error && (
                        <pre className="mb-8 p-4 bg-neutral-900 rounded-lg text-left text-sm text-red-400 max-w-2xl overflow-auto">
                            {error.message}
                            {error.digest && `\nDigest: ${error.digest}`}
                        </pre>
                    )}
                    <button
                        onClick={reset}
                        className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-neutral-950"
                    >
                        Try Again
                    </button>
                </div>
            </body>
        </html>
    );
}

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
    variable: "--font-inter",
    subsets: ["latin"],
    display: "swap",
    axes: ["opsz"],
});

export const metadata: Metadata = {
    title: "SilverSentinel | Autonomous Narrative-Driven Silver Trading",
    description: "Detect market-moving stories days before they impact the price. SilverSentinel leverages AI to trade stories, not just charts.",
};

import BackgroundDots from "@/components/BackgroundDots";
import SmoothScroll from "@/components/SmoothScroll";
import Footer from "@/sections/Footer";
import { AuthProvider } from "@/context/AuthContext";
import { ToastProvider } from "@/components/Toast";

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body
                className={`${inter.variable} font-sans antialiased bg-neutral-950 text-white`}
            >
                <div className="fixed top-0 left-0 w-full h-24 bg-gradient-to-b from-neutral-950 to-transparent backdrop-blur-md z-[60] pointer-events-none [mask-image:linear-gradient(to_bottom,black,transparent)]" />
                <div className="fixed bottom-0 left-0 w-full h-24 bg-gradient-to-t from-neutral-950 to-transparent backdrop-blur-md z-[60] pointer-events-none [mask-image:linear-gradient(to_top,black,transparent)]" />
                <AuthProvider>
                    <ToastProvider>
                        <BackgroundDots />
                        <SmoothScroll>
                            {children}
                            <Footer />
                        </SmoothScroll>
                    </ToastProvider>
                </AuthProvider>
            </body>
        </html>
    );
}

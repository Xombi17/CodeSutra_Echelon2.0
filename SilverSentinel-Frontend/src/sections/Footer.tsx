"use client";



const footerLinks = [
    { href: "#", label: "Contact" },
    { href: "#", label: "Privacy Policy" },
    { href: "#", label: "Terms of Service" },
    { href: "#", label: "Status" },
];

export default function Footer() {
    return (
        <footer className="py-12 border-t border-white/10 bg-neutral-950 relative z-10 overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-silver-500/5 rounded-full blur-[100px] -z-10" />
            <div className="container max-w-none px-6 md:px-12">
                <div className="flex flex-col md:flex-row justify-between items-center gap-8">
                    <div className="flex flex-col items-center md:items-start gap-4">
                        <div className="text-2xl font-bold tracking-tighter text-white">
                            SilverSentinel
                        </div>
                        <p className="text-white/50 text-sm max-w-xs text-center md:text-left">
                            The world&apos;s first autonomous narrative-driven silver trading agent.
                        </p>
                    </div>
                    <div className="flex flex-wrap justify-center gap-8">
                        {footerLinks.map((link) => (
                            <a
                                key={link.label}
                                href={link.href}
                                className="text-white/50 text-sm hover:text-neon-blue transition-colors"
                            >
                                {link.label}
                            </a>
                        ))}
                    </div>
                </div>
                <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
                    <p className="text-white/20 text-[10px] text-center uppercase tracking-widest">
                        &copy; {new Date().getFullYear()} SilverSentinel. PROACTIVE STABILITY PS-14.
                    </p>
                </div>
            </div>
        </footer>
    );
}

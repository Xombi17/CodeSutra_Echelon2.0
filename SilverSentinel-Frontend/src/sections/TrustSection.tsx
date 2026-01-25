

const trustItems = [
    {
        title: "Bank-Grade Security",
        description: "Your data is encrypted with military-grade 256-bit encryption.",
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
            </svg>
        ),
    },
    {
        title: "Real-time Verification",
        description: "Instant analysis of silver purity and weight via computer vision.",
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
        ),
    },
    {
        title: "Autonomous Trading",
        description: "AI agents execute trades based on narrative analysis.",
        icon: (
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
        ),
    },
];

export default function TrustSection() {
    return (
        <section className="py-24 bg-neutral-950">
            <div className="container">
                <h2 className="text-4xl font-medium text-center tracking-tighter text-white mb-16">
                    Trusted Precision
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {trustItems.map((item, index) => (
                        <div
                            key={index}
                            className="glass-panel p-8 rounded-2xl border border-white/10 hover:border-white/20 transition-all duration-300 group"
                        >
                            <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center mb-6 text-white group-hover:scale-110 transition-transform">
                                {item.icon}
                            </div>
                            <h3 className="text-xl font-medium text-white mb-2">{item.title}</h3>
                            <p className="text-white/60">{item.description}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

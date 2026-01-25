"use client";

import React, { useRef, useEffect } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { cn } from "@/lib/utils";

gsap.registerPlugin(ScrollTrigger);

export default function Introduction() {
    const containerRef = useRef(null);
    const textRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const textElement = textRef.current;
        if (!textElement) return;

        // Split text into words (simple span wrap)
        const text = textElement.innerText;
        textElement.innerHTML = "";
        const words = text.split(/\s+/);
        words.forEach((word, i) => {
            const span = document.createElement("span");
            span.innerText = word;
            // Check if it's the last word (which is "conviction.")
            const isLast = i === words.length - 1;
            span.className = cn(
                "opacity-20 inline-block",
                isLast && "text-lime-400"
            );
            textElement.appendChild(span);

            // Add space between words
            const space = document.createTextNode(" ");
            textElement.appendChild(space);
        });

        const spans = textElement.querySelectorAll("span");

        gsap.to(spans, {
            scrollTrigger: {
                trigger: containerRef.current,
                start: "top 80%",
                end: "bottom 50%",
                scrub: 1,
            },
            opacity: 1,
            stagger: 0.1,
            ease: "power2.out",
        });
    }, []);

    return (
        <div ref={containerRef} className="min-h-screen flex items-center justify-center bg-transparent py-10">
            <div className="max-w-none w-full px-6 md:px-20">
                <h2
                    ref={textRef}
                    className={cn("text-4xl md:text-7xl font-bold text-white leading-tight text-center w-full")}
                >
                    In the age of infinite noise, the signal is silver.
                    We identify narrative lifecycles before they break into the mainstream, revealing hidden momentum shifts across culture, markets, and technology. In a world driven by chaos and speed, we give you the clarity to move first—and move with conviction.
                </h2>
            </div>
        </div>
    );
}
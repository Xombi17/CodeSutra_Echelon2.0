import type { Config } from "tailwindcss";

const config: Config = {
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/sections/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        container: {
            center: true,
            padding: {
                DEFAULT: "1rem",
                md: "2rem",
                lg: "4rem",
            },
        },
        fontFamily: {
            sans: ["var(--font-inter)", "sans-serif"],
        },
        screens: {
            sm: "375px",
            md: "768px",
            lg: "1200px",
        },
        extend: {
            colors: {
                lime: {
                    400: "hsl(77, 100%, 65%)",
                },
                silver: {
                    DEFAULT: "hsl(0, 0%, 85%)",
                    500: "hsl(0, 0%, 60%)",
                    700: "hsl(0, 0%, 40%)",
                },
                neon: {
                    blue: "hsl(190, 100%, 50%)",
                    purple: "hsl(270, 100%, 60%)",
                },
            },
            keyframes: {
                "logo-ticker": {
                    from: { transform: "translateX(0)" },
                    to: { transform: "translateX(-50%)" },
                },
            },
            animation: {
                "logo-ticker": "logo-ticker 30s linear infinite",
            },
        },
    },
    plugins: [],
};
export default config;

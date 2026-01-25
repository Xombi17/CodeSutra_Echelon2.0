import Navbar from "@/sections/Navbar";
import Hero from "@/sections/Hero";
// import LogoTicker from "@/sections/LogoTicker"; 
// import Introduction from "@/sections/Introduction";
import Crux from "@/sections/Crux";
import Features from "@/sections/Features";
import TrustSection from "@/sections/TrustSection";
import Integrations from "@/sections/Integrations";
import Faqs from "@/sections/Faqs";

export default function Home() {
    return (
        <>
            <Navbar />
            <Hero />
            {/* <LogoTicker /> */}
            {/* <Introduction /> */}
            <Crux />
            <Features />

            <TrustSection />
            <Integrations />
            <Faqs />
        </>
    );
}

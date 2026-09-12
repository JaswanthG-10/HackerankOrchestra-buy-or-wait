import React, { useState, useEffect } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { Sparkles, ArrowRight, ShieldCheck, TrendingUp, Layers, Zap } from 'lucide-react';

export const Intro3D = ({ onEnter }) => {
  const [isHovered, setIsHovered] = useState(false);

  // Mouse position values for 3D tilt
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Smooth spring physics for 3D rotation
  const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [15, -15]), { stiffness: 200, damping: 20 });
  const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-15, 15]), { stiffness: 200, damping: 20 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    mouseX.set(x);
    mouseY.set(y);
  };

  const handleMouseLeave = () => {
    mouseX.set(0);
    mouseY.set(0);
  };

  return (
    <div
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#070A12] text-white overflow-hidden select-none perspective-1000"
    >
      {/* Dynamic 3D Background Lighting & Starfield / Particle Radiance */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-radial from-[#D97706]/20 via-[#1D4ED8]/15 to-transparent blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-[#059669]/15 blur-[100px] rounded-full" />
        <div className="absolute top-10 left-10 w-80 h-80 bg-[#38BDF8]/15 blur-[90px] rounded-full" />

        {/* Ambient floating gold dust dots */}
        {[...Array(24)].map((_, i) => (
          <motion.div
            key={i}
            initial={{
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1200),
              y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 800),
              opacity: Math.random() * 0.7 + 0.2,
              scale: Math.random() * 0.8 + 0.4,
            }}
            animate={{
              y: ['-20px', '20px', '-20px'],
              opacity: [0.3, 0.8, 0.3],
            }}
            transition={{
              repeat: Infinity,
              duration: 3 + Math.random() * 4,
              ease: 'easeInOut',
            }}
            className="absolute w-1.5 h-1.5 rounded-full bg-gradient-to-r from-[#FBBF24] to-[#F59E0B] shadow-[0_0_8px_#FBBF24]"
          />
        ))}
      </div>

      {/* Main 3D Card with Tilt */}
      <motion.div
        style={{ rotateX, rotateY, transformStyle: 'preserve-3d' }}
        className="relative z-10 max-w-xl w-full mx-4 p-8 sm:p-12 rounded-3xl bg-gradient-to-b from-[#131B2E]/90 to-[#0B101D]/90 border border-[#D97706]/35 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.8),0_0_35px_rgba(217,119,6,0.2)] backdrop-blur-2xl text-center flex flex-col items-center"
      >
        {/* Floating 3D Golden Rupee / Oracle Vault Talisman */}
        <motion.div
          style={{ transform: 'translateZ(60px)' }}
          animate={{
            y: [0, -10, 0],
            rotateZ: [0, 2, -2, 0],
          }}
          transition={{
            repeat: Infinity,
            duration: 4,
            ease: 'easeInOut',
          }}
          className="relative w-28 h-28 mb-6 flex items-center justify-center"
        >
          {/* Outer rotating golden gear ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 12, ease: 'linear' }}
            className="absolute inset-0 rounded-full border-2 border-dashed border-[#FBBF24]/60 shadow-[0_0_25px_rgba(245,158,11,0.4)]"
          />

          {/* Secondary counter-rotating sapphire ring */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ repeat: Infinity, duration: 18, ease: 'linear' }}
            className="absolute inset-2 rounded-full border border-[#38BDF8]/50"
          />

          {/* 3D Core Sphere with Glowing Rupee */}
          <div className="relative w-16 h-16 rounded-full bg-gradient-to-tr from-[#B45309] via-[#F59E0B] to-[#FDE68A] shadow-[0_0_30px_#F59E0B] flex items-center justify-center text-3xl font-headline text-[#0B101D] font-bold border-2 border-[#FEF3C7]">
            ₹
          </div>
        </motion.div>

        {/* 3D Title Block */}
        <motion.div style={{ transform: 'translateZ(45px)' }} className="space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#D97706]/15 border border-[#F59E0B]/40 text-[#FBBF24] text-xs font-semibold uppercase tracking-widest shadow-xs">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Financial Intelligence 2026</span>
          </div>

          <h1 className="font-headline text-4xl sm:text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-[#FFFFFF] via-[#FDE68A] to-[#F59E0B] drop-shadow-md">
            Buy or Wait?
          </h1>

          <p className="text-sm sm:text-base text-slate-300 max-w-md mx-auto leading-relaxed">
            Personal affordability oracle powered by Gemini & Groq. Simulate 90 days of cash flow before spending a single Rupee.
          </p>
        </motion.div>

        {/* 3 Value Pillars in 3D */}
        <motion.div
          style={{ transform: 'translateZ(30px)' }}
          className="grid grid-cols-3 gap-2 sm:gap-3 w-full my-8 text-left"
        >
          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
            <ShieldCheck className="w-4 h-4 text-[#10B981] mb-1" />
            <div className="text-[11px] font-semibold text-white">Floor Guard</div>
            <div className="text-[10px] text-slate-400">Protects ₹8L reserve</div>
          </div>
          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
            <TrendingUp className="w-4 h-4 text-[#38BDF8] mb-1" />
            <div className="text-[11px] font-semibold text-white">90-Day Trajectory</div>
            <div className="text-[10px] text-slate-400">Monte Carlo forecast</div>
          </div>
          <div className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
            <Zap className="w-4 h-4 text-[#F59E0B] mb-1" />
            <div className="text-[11px] font-semibold text-white">Live AI Analysis</div>
            <div className="text-[10px] text-slate-400">Gemini & Groq core</div>
          </div>
        </motion.div>

        {/* Enter Button with 3D Depth */}
        <motion.div style={{ transform: 'translateZ(50px)' }} className="w-full flex flex-col items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.04, boxShadow: '0 0 35px rgba(245,158,11,0.6)' }}
            whileTap={{ scale: 0.96 }}
            onClick={onEnter}
            className="w-full py-4 px-8 rounded-2xl bg-gradient-to-r from-[#D97706] via-[#F59E0B] to-[#B45309] text-[#0B101D] font-bold text-base flex items-center justify-center gap-2 cursor-pointer shadow-[0_10px_30px_rgba(217,119,6,0.4)] transition-all border border-[#FEF3C7]"
          >
            <span>Enter Financial Oracle</span>
            <ArrowRight className="w-5 h-5 stroke-[2.5]" />
          </motion.button>

          <button
            onClick={onEnter}
            className="text-xs text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            Skip intro & proceed to workspace
          </button>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Intro3D;

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2, BrainCircuit, Sparkles } from 'lucide-react';
import { formatINR } from '../theme/tokens';

export const AnalyzingScreen = ({ onComplete, requestData }) => {
  const [step1Status, setStep1Status] = useState('spinning');
  const [step2Status, setStep2Status] = useState('pending');
  const [step3Status, setStep3Status] = useState('pending');

  useEffect(() => {
    const t1 = setTimeout(() => {
      setStep1Status('completed');
      setStep2Status('spinning');
    }, 850);

    const t2 = setTimeout(() => {
      setStep2Status('completed');
      setStep3Status('spinning');
    }, 1750);

    const t3 = setTimeout(() => {
      setStep3Status('completed');
    }, 2500);

    const t4 = setTimeout(() => {
      if (onComplete) onComplete();
    }, 2850);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
    };
  }, [onComplete]);

  const steps = [
    {
      id: 1,
      title: 'Connecting to Indian Banking Feeds',
      sub: 'Liquid balance confirmed · ₹12,40,000',
      status: step1Status,
    },
    {
      id: 2,
      title: 'Running 90-day cash-flow & AI model',
      sub: 'Gemini & Groq evaluated 847 liquidity trajectories',
      status: step2Status,
    },
    {
      id: 3,
      title: 'Synthesizing safe payment strategy',
      sub: '3 optimized payment structures ready',
      status: step3Status,
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center p-6 bg-[var(--bg-app)] theme-transition">
      <div className="ambient-bg" />

      <div className="w-full max-w-md mx-auto flex flex-col items-center z-10">
        {/* Spinning Royal Gold & Sapphire Orb */}
        <div className="relative w-32 h-32 flex items-center justify-center mb-8">
          {/* Outer rotating gold conic ring */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 2.2, ease: 'linear' }}
            className="absolute inset-0 rounded-full"
            style={{
              background: 'conic-gradient(from 0deg, var(--color-gold), transparent 70%)',
              maskImage: 'radial-gradient(circle, transparent 58%, black 62%)',
              WebkitMaskImage: 'radial-gradient(circle, transparent 58%, black 62%)',
            }}
          />

          {/* Counter-rotating sapphire ring */}
          <motion.div
            animate={{ rotate: -360 }}
            transition={{ repeat: Infinity, duration: 3.5, ease: 'linear' }}
            className="absolute inset-2 rounded-full"
            style={{
              background: 'conic-gradient(from 180deg, var(--color-primary), transparent 70%)',
              maskImage: 'radial-gradient(circle, transparent 58%, black 62%)',
              WebkitMaskImage: 'radial-gradient(circle, transparent 58%, black 62%)',
            }}
          />

          {/* Central orb with pulsing Rupee */}
          <div className="relative w-16 h-16 rounded-full bg-[var(--bg-card)] border-2 border-[var(--color-gold)]/50 flex items-center justify-center shadow-xl">
            <motion.div
              animate={{
                scale: [1, 1.25, 1],
                opacity: [0.8, 1, 0.8],
              }}
              transition={{ repeat: Infinity, duration: 1.4, ease: 'easeInOut' }}
              className="text-2xl font-headline font-bold text-[var(--color-gold)]"
            >
              ₹
            </motion.div>
          </div>
        </div>

        {/* Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-[var(--color-gold)]/15 border border-[var(--color-gold)]/30 text-[var(--color-gold)] text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Affordability Engine</span>
          </div>
          <h2 className="font-headline text-2xl sm:text-3xl font-normal text-[var(--text-primary)]">
            Evaluating Cash Flow
          </h2>
          <p className="text-scale-body text-[var(--text-secondary)] mt-1 truncate max-w-xs sm:max-w-sm">
            {requestData?.title ? `Simulating “${requestData.title}” (${formatINR(requestData.amount)})` : 'Simulating 90-day INR cash flow'}
          </p>
        </div>

        {/* Sequential Step Cards */}
        <div className="w-full space-y-3">
          {steps.map((step, idx) => {
            const isActive = step.status === 'spinning';
            const isCompleted = step.status === 'completed';

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 15, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{
                  type: 'spring',
                  stiffness: 300,
                  damping: 26,
                  delay: idx * 0.12,
                }}
                className={`p-4 rounded-2xl border transition-all duration-300 flex items-center gap-3.5 ${
                  isActive
                    ? 'bg-[var(--color-primary)]/10 border-[var(--color-primary)] shadow-md'
                    : isCompleted
                    ? 'bg-[var(--bg-card)] border-[var(--border-color)] opacity-95 shadow-2xs'
                    : 'bg-[var(--bg-card-subtle)] border-[var(--border-color)] opacity-50'
                }`}
              >
                <div className="shrink-0">
                  {isCompleted ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: 'spring', stiffness: 450, damping: 20 }}
                      className="w-7 h-7 rounded-full bg-[var(--color-safe)]/20 border border-[var(--color-safe)] flex items-center justify-center text-[var(--color-safe)] shadow-2xs"
                    >
                      <Check className="w-4 h-4 stroke-[2.5]" />
                    </motion.div>
                  ) : isActive ? (
                    <div className="w-7 h-7 rounded-full bg-[var(--color-primary)]/20 border border-[var(--color-primary)] flex items-center justify-center text-[var(--color-primary)]">
                      <Loader2 className="w-4 h-4 animate-spin stroke-[2.5]" />
                    </div>
                  ) : (
                    <div className="w-7 h-7 rounded-full bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center justify-center text-[var(--text-muted)] text-xs font-semibold">
                      {step.id}
                    </div>
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <h4
                    className={`text-scale-body font-medium transition-colors ${
                      isActive
                        ? 'text-[var(--text-primary)] font-semibold'
                        : isCompleted
                        ? 'text-[var(--text-primary)]'
                        : 'text-[var(--text-secondary)]'
                    }`}
                  >
                    {step.title}
                  </h4>
                  <p className="text-scale-caption text-[var(--text-secondary)] mt-0.5">
                    {step.status === 'pending' ? 'Waiting in queue...' : step.sub}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AnalyzingScreen;

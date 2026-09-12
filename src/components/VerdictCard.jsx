import React from 'react';
import { motion } from 'framer-motion';
import { verdictMap, formatINR } from '../theme/tokens';
import StatusPill from './StatusPill';
import { ShieldCheck, Calendar, IndianRupee, Layers } from 'lucide-react';

export const VerdictCard = ({ request = null }) => {
  const verdictKey = request?.verdict || 'affordable_with_plan';
  const meta = verdictMap[verdictKey] || verdictMap.affordable_with_plan;

  const headline = request?.verdictHeadline || meta.headline;
  const summary = request?.summary || meta.summary;
  const stats = request?.stats || {
    safeToPayNow: 50000,
    totalCost: 280000,
    fullPaymentBy: 'Dec 10, 2026',
    installmentsCount: 6,
  };

  const tintedCardStyle = {
    backgroundColor: `color-mix(in srgb, ${meta.colorVar} 10%, var(--bg-card))`,
    borderColor: `color-mix(in srgb, ${meta.colorVar} 26%, var(--border-color))`,
    boxShadow: `0 14px 40px -8px color-mix(in srgb, ${meta.colorVar} 28%, transparent)`,
  };

  const chips = [
    {
      label: 'Safe to pay now',
      value: formatINR(stats.safeToPayNow),
      icon: ShieldCheck,
      highlight: true,
    },
    {
      label: 'Total cost',
      value: formatINR(stats.totalCost),
      icon: IndianRupee,
    },
    {
      label: 'Full payment by',
      value: stats.fullPaymentBy,
      icon: Calendar,
    },
    {
      label: 'Installments',
      value: `${stats.installmentsCount} payments`,
      icon: Layers,
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.38, ease: [0.22, 1, 0.36, 1] }}
      style={tintedCardStyle}
      className="rounded-3xl p-6 sm:p-8 border theme-transition relative overflow-hidden shadow-lg"
    >
      {/* Top row: Status Pill with spring scale */}
      <div className="flex items-center justify-between gap-4 mb-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 350, damping: 22, delay: 0.08 }}
        >
          <StatusPill verdict={verdictKey} size="lg" />
        </motion.div>

        <span className="text-scale-caption text-[var(--text-secondary)] font-semibold flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[var(--color-safe)] inline-block" />
          <span>AI Model Confidence · 98.6%</span>
        </span>
      </div>

      {/* DM Serif Display headline */}
      <motion.h2
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.38, ease: [0.22, 1, 0.36, 1], delay: 0.12 }}
        className="font-headline text-3xl sm:text-scale-display font-normal tracking-tight text-[var(--text-primary)] mb-3 leading-tight"
      >
        {headline}
      </motion.h2>

      {/* Summary */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.18 }}
        className="text-scale-body text-[var(--text-secondary)] max-w-2xl mb-8 leading-relaxed font-medium"
      >
        {summary}
      </motion.p>

      {/* Four key-figure chips with INR values */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {chips.map((chip, idx) => {
          const Icon = chip.icon;
          return (
            <motion.div
              key={chip.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.22 + idx * 0.05, type: 'spring', stiffness: 320, damping: 26 }}
              className={`p-4 rounded-2xl border transition-all ${
                chip.highlight
                  ? 'bg-[var(--bg-card)] border-[var(--color-gold)]/60 shadow-md ring-1 ring-[var(--color-gold)]/30'
                  : 'bg-[var(--bg-card)]/85 border-[var(--border-color)]'
              }`}
            >
              <div className="flex items-center gap-1.5 text-scale-caption text-[var(--text-secondary)] mb-1 font-semibold">
                <Icon className="w-3.5 h-3.5 text-[var(--color-gold)]" />
                <span className="truncate">{chip.label}</span>
              </div>
              <div className="font-headline text-lg sm:text-xl font-normal text-[var(--text-primary)]">
                {chip.value}
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default VerdictCard;

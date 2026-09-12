import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { motionTokens } from '../theme/tokens';
import VerdictCard from '../components/VerdictCard';
import ForecastChart from '../components/ForecastChart';
import PaymentPlanCard from '../components/PaymentPlanCard';
import SpendingChangesCard from '../components/SpendingChangesCard';
import ExplanationAccordion from '../components/ExplanationAccordion';
import { sampleRequest } from '../data/mockData';
import { Sparkles, ArrowLeft, CheckCircle2, Send, Share2 } from 'lucide-react';

export const ResultScreen = ({ currentRequest = sampleRequest, onBackToAsk, onOpenOverview }) => {
  const [ctaConfirmed, setCtaConfirmed] = useState(false);

  const req = currentRequest || sampleRequest;
  const ctaLabel = req?.stats?.ctaLabel || 'Set Up Installments';

  const handleCtaClick = () => {
    setCtaConfirmed(true);
    setTimeout(() => {
      setCtaConfirmed(false);
    }, 4500);
  };

  return (
    <motion.div
      variants={motionTokens.staggerContainer}
      initial="hidden"
      animate="show"
      exit={{ opacity: 0, y: -12 }}
      className="max-w-5xl mx-auto px-4 sm:px-6 pt-4 sm:pt-8 pb-32 space-y-6"
    >
      {/* Top back / breadcrumb bar */}
      <motion.div
        variants={motionTokens.staggerItem}
        className="flex items-center justify-between py-1"
      >
        <button
          onClick={onBackToAsk}
          className="inline-flex items-center gap-1.5 text-scale-label font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>New Inquiry</span>
        </button>

        <div className="flex items-center gap-3 text-scale-caption text-[var(--text-muted)]">
          <span>Inquiry ID: #{req.id || 'REQ-8472'}</span>
          <span>·</span>
          <span>{req.category}</span>
        </div>
      </motion.div>

      {/* 1. Verdict Hero Card */}
      <motion.div variants={motionTokens.staggerItem}>
        <VerdictCard request={req} />
      </motion.div>

      {/* 2. Forecast Chart Card */}
      <motion.div variants={motionTokens.staggerItem}>
        <ForecastChart height={320} />
      </motion.div>

      {/* 3. Payment Plan Card */}
      <motion.div variants={motionTokens.staggerItem}>
        <PaymentPlanCard />
      </motion.div>

      {/* 4. Spending Changes Card */}
      <motion.div variants={motionTokens.staggerItem}>
        <SpendingChangesCard />
      </motion.div>

      {/* 5. "Why this recommendation" Accordion */}
      <motion.div variants={motionTokens.staggerItem}>
        <ExplanationAccordion />
      </motion.div>

      {/* 6. Primary CTA: full width, teal, glow shadow, spring physics */}
      <motion.div variants={motionTokens.staggerItem} className="pt-2">
        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          transition={{ type: 'spring', stiffness: 350, damping: 25 }}
          type="button"
          onClick={handleCtaClick}
          className="w-full py-4 px-6 rounded-2xl bg-[var(--color-primary)] text-white font-semibold text-scale-body flex items-center justify-center gap-2 glow-teal cursor-pointer select-none shadow-lg transition-all"
        >
          <Sparkles className="w-5 h-5" />
          <span>{ctaLabel}</span>
        </motion.button>

        {/* Confirmation banner when clicked */}
        {ctaConfirmed && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8 }}
            className="mt-3 p-3.5 rounded-xl bg-[var(--color-safe)]/15 border border-[var(--color-safe)]/30 text-[var(--color-safe)] text-scale-label font-medium flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>Payment schedule initialized! Linked to your primary checking (*4821).</span>
            </div>
            <button
              onClick={onOpenOverview}
              className="underline text-scale-caption hover:opacity-80 cursor-pointer"
            >
              View in Overview
            </button>
          </motion.div>
        )}

        <p className="text-center text-scale-caption text-[var(--text-muted)] mt-2.5">
          Guaranteed protection · Automatic cash reserve monitoring prevents overdrafts
        </p>
      </motion.div>
    </motion.div>
  );
};

export default ResultScreen;

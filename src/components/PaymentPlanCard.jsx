import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { sampleInstallments, formatINR } from '../data/mockData';
import { Check, ChevronDown, Calendar, CreditCard, Layers } from 'lucide-react';

export const PaymentPlanCard = ({ installments = sampleInstallments }) => {
  const [expandedId, setExpandedId] = useState(null);

  const totalAmount = installments.reduce((acc, curr) => acc + curr.amount, 0);
  const paidAmount = installments
    .filter((i) => i.status === 'paid')
    .reduce((acc, curr) => acc + curr.amount, 0);
  const progressPercent = Math.round((paidAmount / totalAmount) * 100);

  const toggleExpand = (id) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="glass-card rounded-3xl p-6 sm:p-7 border border-[var(--border-color)] theme-transition relative overflow-hidden shadow-lg">
      {/* Header & Progress Summary */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[var(--color-primary)]/15 text-[var(--color-primary)] flex items-center justify-center">
              <Layers className="w-3.5 h-3.5" />
            </span>
            <h3 className="font-headline text-xl sm:text-2xl font-normal text-[var(--text-primary)]">
              Recommended Installment Schedule (INR)
            </h3>
          </div>
          <p className="text-scale-label text-[var(--text-secondary)]">
            Spreading ₹2,80,000 across 6 scheduled payments preserves continuous cash liquidity
          </p>
        </div>

        <div className="flex items-baseline gap-2 self-start sm:self-auto">
          <span className="font-headline text-2xl font-normal text-[var(--text-primary)]">
            {formatINR(paidAmount)}
          </span>
          <span className="text-scale-caption text-[var(--text-secondary)] font-medium">
            of {formatINR(totalAmount)} ({progressPercent}%)
          </span>
        </div>
      </div>

      {/* Progress Bar Animating 0% -> actual on mount */}
      <div className="w-full h-2.5 bg-[var(--bg-card-subtle)] rounded-full overflow-hidden border border-[var(--border-subtle)] mb-6">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progressPercent}%` }}
          transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
          className="h-full bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-gold)] rounded-full relative"
        >
          <div className="absolute inset-0 bg-white/20 animate-pulse" />
        </motion.div>
      </div>

      {/* Installment Chips wrapped row */}
      <div className="flex flex-wrap gap-2.5">
        {installments.map((item) => {
          const isPaid = item.status === 'paid';
          const isExpanded = expandedId === item.id;

          return (
            <div key={item.id} className="flex-1 min-w-[140px] max-w-[220px]">
              <motion.button
                type="button"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => toggleExpand(item.id)}
                className={`w-full p-3.5 rounded-2xl border text-left transition-all duration-200 cursor-pointer relative ${
                  isPaid
                    ? 'bg-[var(--bg-card-subtle)] border-[var(--border-subtle)] opacity-75 hover:opacity-95'
                    : 'bg-[var(--bg-card)] border-[var(--color-gold)]/50 shadow-md ring-1 ring-[var(--color-gold)]/20 hover:ring-[var(--color-gold)]/50'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-scale-caption font-bold text-[var(--text-secondary)]">
                    Payment #{item.number}
                  </span>
                  {isPaid ? (
                    <span className="flex items-center gap-1 text-[10px] text-[var(--color-safe)] font-bold px-2 py-0.5 rounded-full bg-[var(--color-safe)]/15">
                      <Check className="w-2.5 h-2.5 stroke-[3]" />
                      Paid
                    </span>
                  ) : (
                    <span className="text-[10px] text-[var(--color-gold)] font-bold px-2 py-0.5 rounded-full bg-[var(--color-gold)]/15">
                      Scheduled
                    </span>
                  )}
                </div>

                <div className="flex items-baseline justify-between">
                  <div className="font-headline text-lg font-normal text-[var(--text-primary)]">
                    {formatINR(item.amount)}
                  </div>
                  <ChevronDown
                    className={`w-3.5 h-3.5 text-[var(--text-muted)] transition-transform duration-200 ${
                      isExpanded ? 'rotate-180 text-[var(--color-primary)]' : ''
                    }`}
                  />
                </div>

                <div className="text-[11px] text-[var(--text-muted)] mt-0.5 flex items-center gap-1 font-medium">
                  <Calendar className="w-3 h-3" />
                  <span>{item.dueDate}</span>
                </div>
              </motion.button>

              {/* Expandable detail card */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0, marginTop: 0 }}
                    animate={{ opacity: 1, height: 'auto', marginTop: 8 }}
                    exit={{ opacity: 0, height: 0, marginTop: 0 }}
                    transition={{ duration: 0.22, ease: 'easeInOut' }}
                    className="overflow-hidden rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card-subtle)] p-3 text-scale-caption"
                  >
                    <div className="space-y-1.5 text-[var(--text-secondary)]">
                      <div className="flex justify-between">
                        <span className="text-[var(--text-muted)]">Option ID:</span>
                        <span className="font-mono text-[var(--text-primary)] font-bold">
                          {item.optionId}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[var(--text-muted)]">Due Date:</span>
                        <span className="font-semibold text-[var(--text-primary)]">
                          {item.dueDate}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[var(--text-muted)]">Status:</span>
                        <span
                          className={`capitalize font-bold ${
                            isPaid ? 'text-[var(--color-safe)]' : 'text-[var(--color-gold)]'
                          }`}
                        >
                          {item.status}
                        </span>
                      </div>
                      <div className="pt-1 border-t border-[var(--border-subtle)] text-[10px] text-[var(--text-muted)] flex items-center gap-1">
                        <CreditCard className="w-3 h-3 shrink-0" />
                        <span className="truncate">{item.method}</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PaymentPlanCard;

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { initialSpendingChanges, formatINR } from '../data/mockData';
import { Sparkles, X, Check, RefreshCw } from 'lucide-react';

export const SpendingChangesCard = () => {
  const [items, setItems] = useState(() =>
    initialSpendingChanges.map((item) => ({ ...item, isPaused: false }))
  );

  const togglePause = (id) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, isPaused: !item.isPaused } : item
      )
    );
  };

  const removeItem = (id) => {
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  const restoreAll = () => {
    setItems(initialSpendingChanges.map((item) => ({ ...item, isPaused: false })));
  };

  const totalPausedSavings = items
    .filter((item) => item.isPaused)
    .reduce((acc, curr) => acc + curr.monthlySavings, 0);

  return (
    <div className="glass-card rounded-3xl p-6 sm:p-7 border border-[var(--border-color)] theme-transition relative overflow-hidden shadow-lg">
      {/* Header with running total badge in safe green */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 rounded-lg bg-[var(--color-safe)]/15 text-[var(--color-safe)] flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5" />
            </span>
            <h3 className="font-headline text-xl sm:text-2xl font-normal text-[var(--text-primary)]">
              Recommended Spending Adjustments (INR)
            </h3>
          </div>
          <p className="text-scale-label text-[var(--text-secondary)]">
            Temporary trims in discretionary spends widening your buffer during active payment windows
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          {totalPausedSavings > 0 ? (
            <motion.span
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              key={totalPausedSavings}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[var(--color-safe)]/15 border border-[var(--color-safe)]/30 text-[var(--color-safe)] font-bold text-scale-label shadow-xs"
            >
              <Check className="w-3.5 h-3.5 stroke-[2.5]" />
              <span>Saving +{formatINR(totalPausedSavings)}/mo</span>
            </motion.span>
          ) : (
            <span className="text-scale-caption text-[var(--text-muted)] font-semibold px-3 py-1 rounded-full bg-[var(--bg-card-subtle)] border border-[var(--border-color)]">
              Up to +₹8,768/mo available
            </span>
          )}
        </div>
      </div>

      {/* Items List with layout animations for smooth reflow */}
      <motion.div layout className="space-y-2.5">
        <AnimatePresence mode="popLayout">
          {items.map((item) => {
            const isPaused = item.isPaused;

            return (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.92, height: 0, marginBottom: 0 }}
                transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                className={`p-4 rounded-2xl border transition-all duration-200 flex items-center justify-between gap-3 ${
                  isPaused
                    ? 'bg-[var(--bg-card-subtle)] border-[var(--color-safe)]/40 shadow-xs'
                    : 'bg-[var(--bg-card)] border-[var(--border-color)] hover:border-[var(--color-gold)]/40 hover:shadow-xs'
                }`}
              >
                {/* Left: icon, label, sublabel */}
                <div className="flex items-center gap-3.5 min-w-0 flex-1">
                  <div className="w-10 h-10 rounded-xl bg-[var(--bg-card-subtle)] border border-[var(--border-subtle)] flex items-center justify-center text-lg shrink-0">
                    {item.icon}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h4
                        className={`text-scale-body font-medium transition-all ${
                          isPaused
                            ? 'line-through text-[var(--text-muted)]'
                            : 'text-[var(--text-primary)]'
                        }`}
                      >
                        {item.label}
                      </h4>

                      {isPaused && (
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[var(--color-safe)] text-white tracking-wide uppercase"
                        >
                          Paused
                        </motion.span>
                      )}
                    </div>

                    <p className="text-scale-caption text-[var(--text-secondary)] mt-0.5 truncate">
                      {item.subLabel}
                    </p>
                  </div>
                </div>

                {/* Right: saves ₹X/mo + Pause toggle + Dismiss button */}
                <div className="flex items-center gap-2.5 shrink-0">
                  <div className="text-right">
                    <span className="text-scale-label font-bold text-[var(--color-safe)] block">
                      saves {formatINR(item.monthlySavings)}/mo
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => togglePause(item.id)}
                    className={`px-3.5 py-1.5 rounded-xl text-scale-label font-semibold transition-all cursor-pointer ${
                      isPaused
                        ? 'bg-[var(--color-safe)]/15 text-[var(--color-safe)] border border-[var(--color-safe)]/30 hover:bg-[var(--color-safe)]/25'
                        : 'bg-[var(--bg-card-subtle)] text-[var(--text-primary)] border border-[var(--border-color)] hover:border-[var(--color-primary)] hover:text-[var(--color-primary)]'
                    }`}
                  >
                    {isPaused ? 'Resume' : 'Pause'}
                  </button>

                  <button
                    type="button"
                    onClick={() => removeItem(item.id)}
                    title="Dismiss recommendation"
                    className="w-8 h-8 rounded-xl flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card-subtle)] transition-colors cursor-pointer"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {items.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-6 border border-dashed border-[var(--border-color)] rounded-2xl p-4"
          >
            <p className="text-scale-label text-[var(--text-secondary)] mb-2">
              All spending change suggestions dismissed.
            </p>
            <button
              onClick={restoreAll}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-scale-caption font-semibold bg-[var(--bg-card-subtle)] text-[var(--text-primary)] hover:border-[var(--color-primary)] border border-[var(--border-color)] cursor-pointer"
            >
              <RefreshCw className="w-3 h-3" />
              Reset Suggestions
            </button>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default SpendingChangesCard;

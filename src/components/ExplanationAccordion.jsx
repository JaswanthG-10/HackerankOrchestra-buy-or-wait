import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, HelpCircle, ShieldCheck, Activity, CalendarCheck, Percent } from 'lucide-react';
import { sampleRequest } from '../data/mockData';

const tileIcons = [ShieldCheck, Percent, Activity, CalendarCheck];

export const ExplanationAccordion = ({
  whyData = sampleRequest.whyRecommendation,
  defaultOpen = true,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="glass-card rounded-3xl border border-[var(--border-color)] overflow-hidden theme-transition">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 sm:p-7 flex items-center justify-between text-left cursor-pointer hover:bg-[var(--bg-card-subtle)]/40 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center">
            <HelpCircle className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-headline text-xl sm:text-2xl font-normal text-[var(--text-primary)]">
              Why this recommendation?
            </h3>
            <p className="text-scale-label text-[var(--text-secondary)]">
              Underlying algorithm insights, risk thresholds, and buffer reasoning
            </p>
          </div>
        </div>

        {/* Arrow rotates 180° open */}
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.22, ease: 'easeInOut' }}
          className="w-8 h-8 rounded-full bg-[var(--bg-card-subtle)] flex items-center justify-center text-[var(--text-secondary)] border border-[var(--border-subtle)]"
        >
          <ChevronDown className="w-4 h-4" />
        </motion.div>
      </button>

      {/* Height-animated accordion body via AnimatePresence */}
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.26, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-6 sm:px-7 pb-7 pt-1 border-t border-[var(--border-subtle)] space-y-6">
              {/* Plain language explanation paragraph */}
              <p className="text-scale-body text-[var(--text-primary)] leading-relaxed bg-[var(--bg-card-subtle)]/60 p-4 rounded-2xl border border-[var(--border-subtle)]">
                {whyData.plainLanguage}
              </p>

              {/* 4 Stat Tiles */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {whyData.tiles.map((tile, idx) => {
                  const Icon = tileIcons[idx % tileIcons.length];
                  return (
                    <div
                      key={tile.label}
                      className="p-4 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-color)] shadow-2xs space-y-1"
                    >
                      <div className="flex items-center gap-1.5 text-scale-caption text-[var(--text-secondary)] font-medium">
                        <Icon className="w-3.5 h-3.5 text-[var(--color-primary)]" />
                        <span>{tile.label}</span>
                      </div>
                      <div className="font-headline text-2xl font-normal text-[var(--text-primary)]">
                        {tile.value}
                      </div>
                      <div className="text-[11px] text-[var(--text-muted)] font-medium">
                        {tile.sub}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ExplanationAccordion;

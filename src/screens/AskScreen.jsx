import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { exampleQueries, categories, historyItems, formatINR } from '../data/mockData';
import RequestListRow from '../components/RequestListRow';
import { ArrowRight, Sparkles, Zap, BrainCircuit } from 'lucide-react';

export const AskScreen = ({ onStartAnalysis, onSelectHistoryItem }) => {
  const [query, setQuery] = useState('');
  const [amount, setAmount] = useState('280000');
  const [selectedCategory, setSelectedCategory] = useState('Travel');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [displayedPlaceholder, setDisplayedPlaceholder] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  // Typewriter effect cycling through example queries
  useEffect(() => {
    const currentTarget = exampleQueries[placeholderIndex].text;
    let charIdx = 0;
    let timeoutId;

    setDisplayedPlaceholder('');
    setIsTyping(true);

    const typeNextChar = () => {
      if (charIdx <= currentTarget.length) {
        setDisplayedPlaceholder(currentTarget.slice(0, charIdx));
        charIdx++;
        timeoutId = setTimeout(typeNextChar, 35);
      } else {
        setIsTyping(false);
        timeoutId = setTimeout(() => {
          setPlaceholderIndex((prev) => (prev + 1) % exampleQueries.length);
        }, 2500);
      }
    };

    timeoutId = setTimeout(typeNextChar, 100);

    return () => clearTimeout(timeoutId);
  }, [placeholderIndex]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    const finalQuery = query.trim() || exampleQueries[placeholderIndex].text;
    const finalAmount = parseFloat(amount) || exampleQueries[placeholderIndex].amount;

    onStartAnalysis({
      query: finalQuery,
      amount: finalAmount,
      category: selectedCategory,
    });
  };

  const handleChipClick = (cat) => {
    setSelectedCategory(cat);
  };

  const recentRequests = historyItems.slice(0, 4);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.22, ease: 'easeInOut' }}
      className="max-w-4xl mx-auto px-4 sm:px-6 pt-8 sm:pt-12 pb-24"
    >
      {/* Hero Badge with Royal Gold & Sapphire accents */}
      <div className="flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[var(--color-gold)]/40 bg-[var(--color-gold)]/10 text-[var(--color-gold)] text-scale-label font-semibold mb-6 shadow-xs"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--color-gold)] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--color-gold)]"></span>
          </span>
          <BrainCircuit className="w-4 h-4 text-[var(--color-primary)]" />
          <span>Gemini & Groq Financial Oracle · 90-day INR Forecast</span>
        </motion.div>

        {/* Hero Headline: DM Serif Display, 56px */}
        <h1 className="font-headline text-4xl sm:text-[56px] sm:leading-[1.08] font-normal tracking-tight text-[var(--text-primary)] max-w-2xl">
          Can I afford this right now?
        </h1>

        <p className="mt-3 text-scale-body text-[var(--text-secondary)] max-w-lg">
          Ask anything from a Royal Enfield to a Tokyo holiday. Our AI simulates your next 90 days of cash flow before you spend.
        </p>
      </div>

      {/* Main Analysis Input Box */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, type: 'spring', stiffness: 280, damping: 26 }}
        className="mt-10 glass-card rounded-3xl p-5 sm:p-7 shadow-xl border border-[var(--border-color)] theme-transition relative overflow-hidden"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Query Textarea with Typewriter Placeholder */}
          <div>
            <label className="block text-scale-label font-semibold text-[var(--text-primary)] mb-2">
              What do you want to purchase or pay for?
            </label>
            <div className="relative">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={3}
                placeholder={isTyping ? `${displayedPlaceholder}▌` : displayedPlaceholder}
                className="w-full px-4 py-3 rounded-2xl bg-[var(--bg-card-subtle)] border border-[var(--border-color)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 resize-none text-scale-body transition-all"
              />
            </div>
          </div>

          {/* Amount Input with Rupee symbol (₹) + Analyze Button */}
          <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center pt-1">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-lg font-bold text-[var(--color-gold)]">
                ₹
              </div>
              <input
                type="number"
                min="1"
                step="any"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Estimated cost in INR (e.g. 280000)"
                className="w-full pl-9 pr-4 py-3.5 rounded-2xl bg-[var(--bg-card-subtle)] border border-[var(--border-color)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 text-scale-body font-semibold transition-all"
              />
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: 'spring', stiffness: 400, damping: 25 }}
              type="submit"
              className="px-7 py-3.5 rounded-2xl bg-gradient-to-r from-[var(--color-primary)] to-[#1E40AF] text-white font-bold text-scale-body flex items-center justify-center gap-2.5 glow-royal hover:opacity-95 cursor-pointer select-none transition-all shadow-md"
            >
              <Sparkles className="w-4 h-4 text-[#FDE68A]" />
              <span>Analyze Affordability</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>

          {/* Category Chip Row */}
          <div className="pt-2">
            <span className="block text-scale-caption text-[var(--text-secondary)] font-bold mb-2 tracking-wider">
              CATEGORY
            </span>
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => {
                const isActive = selectedCategory === cat;
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => handleChipClick(cat)}
                    className={`px-3.5 py-1.5 rounded-full text-scale-label font-medium transition-all cursor-pointer select-none ${
                      isActive
                        ? 'bg-[var(--color-primary)] text-white shadow-xs font-semibold'
                        : 'bg-[var(--bg-card-subtle)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-[var(--color-primary)] hover:text-[var(--text-primary)]'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>
        </form>
      </motion.div>

      {/* Recent Inquiries Section */}
      <div className="mt-12 space-y-3">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <h3 className="text-scale-label font-bold uppercase tracking-wider text-[var(--text-secondary)]">
              Recent Inquiries
            </h3>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-[var(--bg-card-subtle)] border border-[var(--border-color)] text-[var(--color-gold)] font-bold">
              4 cached
            </span>
          </div>
          <span className="text-scale-caption text-[var(--text-muted)]">
            Click any to review AI verdict
          </span>
        </div>

        <div className="space-y-2.5">
          {recentRequests.map((item) => (
            <RequestListRow
              key={item.id}
              item={item}
              onClick={() => onSelectHistoryItem ? onSelectHistoryItem(item) : onStartAnalysis({ query: item.title, amount: item.amount, category: item.category })}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default AskScreen;

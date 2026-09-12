import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { historyItems, categories } from '../data/mockData';
import RequestListRow from '../components/RequestListRow';
import { Filter, History as HistoryIcon, Search, RotateCcw } from 'lucide-react';

const verdictFilters = [
  { id: 'all', label: 'All Inquiries' },
  { id: 'affordable_now', label: 'Affordable Now' },
  { id: 'affordable_with_plan', label: 'With Plan' },
  { id: 'affordable_later', label: 'Affordable Later' },
  { id: 'not_affordable', label: 'Not Affordable' },
];

export const HistoryScreen = ({ onSelectItem }) => {
  const [selectedVerdict, setSelectedVerdict] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredItems = useMemo(() => {
    return historyItems.filter((item) => {
      const matchVerdict =
        selectedVerdict === 'all' || item.verdict === selectedVerdict;
      const matchCategory =
        selectedCategory === 'all' || item.category === selectedCategory;
      const matchSearch =
        !searchTerm.trim() ||
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.notes.toLowerCase().includes(searchTerm.toLowerCase());

      return matchVerdict && matchCategory && matchSearch;
    });
  }, [selectedVerdict, selectedCategory, searchTerm]);

  const resetFilters = () => {
    setSelectedVerdict('all');
    setSelectedCategory('all');
    setSearchTerm('');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.22, ease: 'easeInOut' }}
      className="max-w-4xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 pb-28 space-y-6"
    >
      {/* Screen Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <span className="text-scale-caption text-[var(--color-gold)] font-bold tracking-wider uppercase">
            INR Inquiry Records
          </span>
          <h1 className="font-headline text-3xl sm:text-4xl font-normal text-[var(--text-primary)] mt-1">
            Affordability History
          </h1>
        </div>

        <span className="text-scale-caption text-[var(--text-secondary)]">
          Showing {filteredItems.length} of {historyItems.length} evaluations
        </span>
      </div>

      {/* Filter Section */}
      <div className="glass-card rounded-2xl p-4 sm:p-5 border border-[var(--border-color)] theme-transition space-y-4 shadow-xs">
        {/* Search bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-[var(--text-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search past inquiries by item, category, or note..."
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[var(--bg-card-subtle)] border border-[var(--border-color)] text-scale-body text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--color-primary)] text-scale-label"
          />
        </div>

        {/* Verdict Filter Pills (active = solid foreground background) */}
        <div>
          <span className="block text-scale-caption font-semibold text-[var(--text-muted)] uppercase mb-2">
            Verdict Status
          </span>
          <div className="flex flex-wrap gap-2">
            {verdictFilters.map((filter) => {
              const isActive = selectedVerdict === filter.id;
              return (
                <button
                  key={filter.id}
                  type="button"
                  onClick={() => setSelectedVerdict(filter.id)}
                  className={`px-3.5 py-1.5 rounded-full text-scale-label font-medium transition-all cursor-pointer select-none ${
                    isActive
                      ? 'bg-[var(--text-primary)] text-[var(--bg-app)] shadow-xs'
                      : 'bg-[var(--bg-card-subtle)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-[var(--border-color)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {filter.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Smaller Category Filter Pills */}
        <div>
          <span className="block text-scale-caption font-semibold text-[var(--text-muted)] uppercase mb-2">
            Category
          </span>
          <div className="flex flex-wrap gap-1.5">
            <button
              type="button"
              onClick={() => setSelectedCategory('all')}
              className={`px-2.5 py-1 rounded-full text-scale-caption font-medium transition-all cursor-pointer ${
                selectedCategory === 'all'
                  ? 'bg-[var(--color-primary)] text-white'
                  : 'bg-[var(--bg-card-subtle)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-[var(--color-primary)]'
              }`}
            >
              All Categories
            </button>
            {categories.map((cat) => {
              const isActive = selectedCategory === cat;
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2.5 py-1 rounded-full text-scale-caption font-medium transition-all cursor-pointer ${
                    isActive
                      ? 'bg-[var(--color-primary)] text-white'
                      : 'bg-[var(--bg-card-subtle)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-[var(--color-primary)]'
                  }`}
                >
                  {cat}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* List using AnimatePresence mode="popLayout" so filtering reflows smoothly */}
      <motion.div layout className="space-y-3">
        <AnimatePresence mode="popLayout">
          {filteredItems.map((item) => (
            <motion.div
              key={item.id}
              layout
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.92 }}
              transition={{ type: 'spring', stiffness: 350, damping: 28 }}
            >
              <RequestListRow
                item={item}
                onClick={() => onSelectItem && onSelectItem(item)}
              />
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredItems.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12 glass-card rounded-2xl border border-[var(--border-color)] p-6 space-y-3"
          >
            <HistoryIcon className="w-8 h-8 text-[var(--text-muted)] mx-auto" />
            <p className="text-scale-body text-[var(--text-secondary)]">
              No inquiries match your current filters.
            </p>
            <button
              onClick={resetFilters}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-scale-label font-medium bg-[var(--bg-card-subtle)] text-[var(--text-primary)] border border-[var(--border-color)] hover:border-[var(--color-primary)] cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset All Filters
            </button>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default HistoryScreen;

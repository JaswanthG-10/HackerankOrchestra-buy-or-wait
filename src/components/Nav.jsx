import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '../theme/ThemeProvider';
import { Sparkles, Sun, Moon, Eye } from 'lucide-react';

export const Nav = ({ currentScreen, setScreen, isAnalyzing = false, onShowIntro = null }) => {
  const { theme, toggleTheme } = useTheme();

  if (isAnalyzing) {
    return null;
  }

  const navLinks = [
    { id: 'ask', label: 'Ask' },
    { id: 'result', label: 'Result' },
    { id: 'dashboard', label: 'Overview' },
    { id: 'history', label: 'History' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full glass-nav theme-transition">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Brand / Logo with Royal Crown / Sparkle badge */}
        <div 
          onClick={() => setScreen('ask')}
          className="flex items-center gap-2.5 cursor-pointer group select-none"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#1D4ED8] to-[#D97706] flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform duration-200 border border-[#FDE68A]/40">
            <Sparkles className="w-4 h-4 text-[#FEF3C7]" />
          </div>
          <div className="flex flex-col">
            <span className="font-headline text-lg font-bold tracking-tight text-[var(--text-primary)] flex items-center gap-1.5">
              <span>Buy or Wait?</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-[var(--color-gold)]/15 border border-[var(--color-gold)]/30 text-[var(--color-gold)] font-bold uppercase tracking-wider">
                INR ₹
              </span>
            </span>
          </div>
        </div>

        {/* Desktop Nav Items */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = currentScreen === link.id;
            return (
              <button
                key={link.id}
                onClick={() => setScreen(link.id)}
                className={`relative px-4 py-2 text-scale-label font-medium rounded-md transition-colors duration-150 cursor-pointer ${
                  isActive
                    ? 'text-[var(--text-primary)] font-semibold'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                {link.label}
                {isActive && (
                  <motion.div
                    layoutId="nav-underline"
                    className="absolute bottom-0 left-2 right-2 h-0.5 bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-gold)] rounded-full"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
              </button>
            );
          })}
        </nav>

        {/* Right side controls: 3D Intro re-trigger, Royal Theme toggle, Avatar */}
        <div className="flex items-center gap-2.5">
          {/* Replay 3D Intro Button */}
          {onShowIntro && (
            <button
              onClick={onShowIntro}
              title="Replay 3D Intro Experience"
              className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-full border border-[var(--border-color)] bg-[var(--bg-card)] text-scale-caption font-semibold text-[var(--text-secondary)] hover:text-[var(--color-primary)] hover:border-[var(--color-primary)] transition-all cursor-pointer shadow-2xs"
            >
              <Eye className="w-3.5 h-3.5 text-[var(--color-gold)]" />
              <span>3D Intro</span>
            </button>
          )}

          {/* Theme Toggle Pill */}
          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[var(--border-color)] bg-[var(--bg-card)] text-scale-label font-medium text-[var(--text-primary)] hover:border-[var(--color-gold)] transition-all cursor-pointer shadow-2xs"
          >
            {theme === 'light' ? (
              <>
                <Sun className="w-3.5 h-3.5 text-[var(--color-gold)]" />
                <span className="text-xs font-semibold">👑 Royal Bright</span>
              </>
            ) : (
              <>
                <Moon className="w-3.5 h-3.5 text-[var(--color-primary)]" />
                <span className="text-xs font-semibold">🌌 Midnight</span>
              </>
            )}
          </button>

          {/* User Avatar */}
          <div 
            title="Jaswanth G · Connected INR Checking Account"
            className="w-9 h-9 rounded-full bg-gradient-to-br from-[var(--color-primary)]/20 to-[var(--color-gold)]/20 border border-[var(--color-gold)]/40 flex items-center justify-center text-[var(--color-gold)] font-bold text-xs cursor-pointer select-none shadow-xs"
          >
            JG
          </div>
        </div>
      </div>
    </header>
  );
};

export default Nav;

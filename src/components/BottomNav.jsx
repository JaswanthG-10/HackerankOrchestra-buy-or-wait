import React from 'react';
import { motion } from 'framer-motion';

export const BottomNav = ({ currentScreen, setScreen, isAnalyzing = false }) => {
  if (isAnalyzing) {
    return null;
  }

  const items = [
    { id: 'ask', label: 'Ask', icon: '💬' },
    { id: 'result', label: 'Result', icon: '📊' },
    { id: 'dashboard', label: 'Overview', icon: '💼' },
    { id: 'history', label: 'History', icon: '📜' },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t border-[var(--border-color)] glass-nav pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2 px-4 theme-transition">
      <div className="flex items-center justify-around">
        {items.map((item) => {
          const isActive = currentScreen === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setScreen(item.id)}
              className="flex flex-col items-center justify-center flex-1 py-1 cursor-pointer transition-colors relative"
            >
              <span className="text-xl mb-0.5 leading-none">{item.icon}</span>
              <span
                className={`text-[11px] font-medium transition-colors ${
                  isActive
                    ? 'text-[var(--color-primary)] font-semibold'
                    : 'text-[var(--text-secondary)]'
                }`}
              >
                {item.label}
              </span>
              {isActive && (
                <motion.div
                  layoutId="bottom-nav-indicator"
                  className="absolute -top-2 w-8 h-1 bg-[var(--color-primary)] rounded-full"
                  transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNav;

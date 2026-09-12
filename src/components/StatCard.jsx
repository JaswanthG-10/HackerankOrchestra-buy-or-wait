import React from 'react';
import { motion } from 'framer-motion';

export const StatCard = ({
  label,
  value,
  subtitle,
  icon: Icon,
  accentColor = 'var(--text-primary)',
  trend = null,
  badge = null,
}) => {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: 'spring', stiffness: 300, damping: 28 }}
      className="glass-card rounded-2xl p-5 shadow-xs relative overflow-hidden flex flex-col justify-between theme-transition"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {Icon && (
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{
                backgroundColor: `color-mix(in srgb, ${accentColor} 14%, transparent)`,
                color: accentColor,
              }}
            >
              <Icon className="w-4 h-4" />
            </div>
          )}
          <span className="text-scale-label font-medium text-[var(--text-secondary)]">
            {label}
          </span>
        </div>
        {badge && (
          <span className="text-[11px] px-2 py-0.5 rounded-full font-medium border border-[var(--border-color)] bg-[var(--bg-card-subtle)] text-[var(--text-secondary)]">
            {badge}
          </span>
        )}
      </div>

      <div className="space-y-1">
        <div
          className="font-headline text-scale-stat font-normal tracking-tight"
          style={{ color: accentColor }}
        >
          {value}
        </div>
        {subtitle && (
          <p className="text-scale-caption text-[var(--text-muted)] font-medium">
            {subtitle}
          </p>
        )}
      </div>

      {trend && (
        <div className="mt-3 pt-3 border-t border-[var(--border-subtle)] flex items-center gap-1.5 text-scale-caption text-[var(--text-secondary)]">
          {trend}
        </div>
      )}
    </motion.div>
  );
};

export default StatCard;

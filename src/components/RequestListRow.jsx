import React from 'react';
import { motion } from 'framer-motion';
import StatusPill from './StatusPill';
import { formatINR } from '../theme/tokens';

export const RequestListRow = ({
  item,
  onClick = null,
  compact = false,
}) => {
  return (
    <motion.div
      whileHover={{ x: 4 }}
      transition={{ type: 'spring', stiffness: 300, damping: 28 }}
      onClick={onClick}
      className={`group flex items-center justify-between p-3.5 sm:p-4 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] hover:border-[var(--color-primary)] hover:shadow-md transition-all cursor-pointer select-none theme-transition shadow-2xs ${
        compact ? 'py-2.5' : ''
      }`}
    >
      <div className="flex items-center gap-3.5 min-w-0 pr-3">
        <div className="w-10 h-10 rounded-xl bg-[var(--bg-card-subtle)] flex items-center justify-center text-lg shrink-0 border border-[var(--border-subtle)]">
          {item.emoji || '💳'}
        </div>
        <div className="min-w-0">
          <h4 className="text-scale-body font-medium text-[var(--text-primary)] truncate group-hover:text-[var(--color-primary)] transition-colors">
            {item.title}
          </h4>
          <div className="flex items-center gap-2 text-scale-caption text-[var(--text-secondary)] mt-0.5">
            <span>{item.date}</span>
            <span>·</span>
            <span className="font-semibold text-[var(--color-gold)]">{item.category}</span>
            {item.notes && (
              <>
                <span className="hidden sm:inline">·</span>
                <span className="hidden sm:inline truncate max-w-[220px]">{item.notes}</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <div className="text-right">
          <span className="text-scale-body font-bold text-[var(--text-primary)]">
            {formatINR(item.amount)}
          </span>
        </div>
        <StatusPill verdict={item.verdict} size="sm" />
      </div>
    </motion.div>
  );
};

export default RequestListRow;

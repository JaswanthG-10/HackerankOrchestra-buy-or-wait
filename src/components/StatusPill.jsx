import React from 'react';
import { verdictMap } from '../theme/tokens';
import { CheckCircle2, Split, Clock, AlertTriangle } from 'lucide-react';

const icons = {
  affordable_now: CheckCircle2,
  affordable_with_plan: Split,
  affordable_later: Clock,
  not_affordable: AlertTriangle,
};

export const StatusPill = ({ verdict = 'affordable_with_plan', size = 'sm', showIcon = true, customLabel = null }) => {
  const meta = verdictMap[verdict] || verdictMap.affordable_with_plan;
  const IconComponent = icons[verdict] || icons.affordable_with_plan;

  const isLg = size === 'lg';

  // Dynamic color-mix styles matching prompt specs:
  // Background = color-mix(verdict-color 14%, transparent)
  // Text = verdict color variable
  // Border = color-mix(verdict-color 30%, transparent)
  const pillStyle = {
    backgroundColor: `color-mix(in srgb, ${meta.colorVar} 14%, transparent)`,
    color: meta.colorVar,
    borderColor: `color-mix(in srgb, ${meta.colorVar} 30%, transparent)`,
  };

  return (
    <span
      style={pillStyle}
      className={`inline-flex items-center gap-1.5 font-medium border rounded-full transition-all duration-200 ${
        isLg ? 'px-3.5 py-1.5 text-scale-label font-semibold shadow-xs' : 'px-2.5 py-0.5 text-scale-caption'
      }`}
    >
      {showIcon && <IconComponent className={isLg ? 'w-4 h-4' : 'w-3 h-3'} />}
      <span>{customLabel || meta.label}</span>
    </span>
  );
};

export default StatusPill;

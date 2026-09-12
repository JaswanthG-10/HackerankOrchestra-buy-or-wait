import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceDot,
} from 'recharts';
import { useTheme } from '../theme/ThemeProvider';
import { forecastPoints, userFinancialProfile, formatINR } from '../data/mockData';

// Custom Tooltip with card styling and INR formatting
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="glass-card rounded-2xl p-3.5 shadow-xl border border-[var(--border-color)] text-left min-w-[220px] z-50">
        <p className="text-scale-caption text-[var(--text-muted)] font-bold mb-1 uppercase tracking-wider">
          {label} · Forecast Point
        </p>
        <div className="flex items-baseline gap-1.5 mb-1.5">
          <span className="font-headline text-xl font-normal text-[var(--color-primary)]">
            {formatINR(data.balance)}
          </span>
          <span className="text-scale-caption text-[var(--text-secondary)] font-medium">est. liquidity</span>
        </div>
        {data.event && (
          <div className="pt-2 border-t border-[var(--border-subtle)] text-scale-caption text-[var(--text-primary)]">
            <span className="font-bold text-[var(--text-secondary)] block mb-0.5">Event:</span>
            {data.isIncome ? (
              <span className="text-[var(--color-safe)] font-semibold">{data.event}</span>
            ) : data.isPaymentDate ? (
              <span className="text-[var(--color-caution)] font-semibold">{data.event}</span>
            ) : (
              <span>{data.event}</span>
            )}
          </div>
        )}
      </div>
    );
  }
  return null;
};

export const ForecastChart = ({ data = forecastPoints, height = 320, isMini = false }) => {
  const { theme } = useTheme();

  const isDark = theme === 'dark';
  const primaryColor = isDark ? '#38BDF8' : '#1D4ED8';
  const cautionColor = isDark ? '#F59E0B' : '#D97706';
  const safeColor = isDark ? '#10B981' : '#059669';
  const cardColor = isDark ? '#131B2E' : '#FFFFFF';
  const axisColor = isDark ? '#64748B' : '#94A3B8';
  const safetyFloor = userFinancialProfile.safetyFloor; // ₹8,00,000

  const paymentDots = data.filter((p) => p.isPaymentDate);

  return (
    <div className="glass-card rounded-3xl p-5 sm:p-7 border border-[var(--border-color)] theme-transition relative overflow-hidden shadow-lg">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <h3 className="font-headline text-xl sm:text-2xl font-normal text-[var(--text-primary)]">
            90-Day Cash-Flow Trajectory (INR ₹)
          </h3>
          <p className="text-scale-label text-[var(--text-secondary)] mt-0.5">
            Monte Carlo simulation including scheduled EMIs, salary credits, and proposed payments
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className="inline-flex items-center gap-1.5 text-scale-caption font-semibold px-3 py-1 rounded-full bg-[var(--color-safe)]/15 text-[var(--color-safe)] border border-[var(--color-safe)]/30">
            Floor Intact (+₹3,53,000 lowest surplus)
          </span>
        </div>
      </div>

      {/* Recharts AreaChart with draw-on animation over 1200ms */}
      <div style={{ height: `${height}px`, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 16, right: 16, left: isMini ? 0 : 5, bottom: 0 }}>
            <defs>
              <linearGradient id="forecastRoyalGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={primaryColor} stopOpacity={0.28} />
                <stop offset="100%" stopColor={primaryColor} stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <XAxis
              dataKey="date"
              stroke={axisColor}
              tickLine={false}
              axisLine={false}
              tick={{ fontSize: 11, fill: axisColor }}
              dy={8}
            />

            {!isMini && (
              <YAxis
                domain={[600000, 2200000]}
                stroke={axisColor}
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 11, fill: axisColor }}
                tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`}
                dx={-4}
              />
            )}

            <Tooltip content={<CustomTooltip />} />

            {/* Dashed amber ReferenceLine for Safety Floor (₹8,00,000) */}
            <ReferenceLine
              y={safetyFloor}
              stroke={cautionColor}
              strokeDasharray="4 4"
              strokeWidth={1.75}
              label={{
                value: `Safety Floor (₹8,00,000)`,
                fill: cautionColor,
                position: 'insideBottomRight',
                fontSize: 11,
                offset: 6,
                fontWeight: 700,
              }}
            />

            {/* Amber ReferenceDots on payment dates */}
            {paymentDots.map((dot) => (
              <ReferenceDot
                key={dot.date}
                x={dot.date}
                y={dot.balance}
                r={5}
                fill={cautionColor}
                stroke={cardColor}
                strokeWidth={2}
                isFront={true}
              />
            ))}

            {/* Area with 1200ms animation */}
            <Area
              type="monotone"
              dataKey="balance"
              stroke={primaryColor}
              strokeWidth={2.8}
              fill="url(#forecastRoyalGradient)"
              isAnimationActive={true}
              animationDuration={1200}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Legend Row */}
      <div className="mt-4 pt-4 border-t border-[var(--border-subtle)] flex flex-wrap items-center justify-between gap-y-2 gap-x-4 text-scale-caption text-[var(--text-secondary)] font-medium">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 rounded-full bg-[var(--color-primary)] inline-block" />
            <span>Liquid Cash Balance</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="w-3 h-0.5 border-b-2 border-dashed inline-block"
              style={{ borderColor: cautionColor }}
            />
            <span>Safety Floor (₹8,00,000)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className="w-2.5 h-2.5 rounded-full inline-block border"
              style={{ backgroundColor: cautionColor, borderColor: cardColor }}
            />
            <span>Payment Dates</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[var(--color-safe)] inline-block" />
            <span>Salary Credits (+₹3,40,000)</span>
          </div>
        </div>

        <span className="text-[var(--text-muted)] text-[11px] font-semibold">
          Simulated range: ₹11,53,000 – ₹19,23,000
        </span>
      </div>
    </div>
  );
};

export default ForecastChart;

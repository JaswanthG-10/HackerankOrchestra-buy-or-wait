import React from 'react';
import { motion } from 'framer-motion';
import { userFinancialProfile, activePlans, upcomingEvents, forecastPoints, formatINR } from '../data/mockData';
import StatCard from '../components/StatCard';
import {
  Wallet,
  Shield,
  CreditCard,
  ArrowUpRight,
  Calendar,
  Layers,
  ChevronRight,
} from 'lucide-react';
import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useTheme } from '../theme/ThemeProvider';

export const DashboardScreen = ({ onNavigateToPlan }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const primaryColor = isDark ? '#38BDF8' : '#1D4ED8';
  const axisColor = isDark ? '#64748B' : '#94A3B8';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.22, ease: 'easeInOut' }}
      className="max-w-5xl mx-auto px-4 sm:px-6 pt-6 sm:pt-10 pb-28 space-y-8"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <span className="text-scale-caption text-[var(--color-gold)] font-bold tracking-wider uppercase">
            Financial Health Overview (INR ₹)
          </span>
          <h1 className="font-headline text-3xl sm:text-4xl font-normal text-[var(--text-primary)] mt-1">
            Cash Reserves & Commitments
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[var(--color-safe)]/15 text-[var(--color-safe)] border border-[var(--color-safe)]/25 text-scale-caption font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-safe)] animate-ping" />
            Live Sync Active
          </span>
        </div>
      </div>

      {/* Three Stat Cards with INR values */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Current Balance"
          value={formatINR(userFinancialProfile.currentBalance)}
          subtitle="Across 2 verified Indian banking accounts"
          icon={Wallet}
          accentColor="var(--color-primary)"
          trend={
            <span className="text-[var(--color-safe)] flex items-center gap-0.5 font-bold">
              <ArrowUpRight className="w-3.5 h-3.5" /> +₹1,24,000 vs last month
            </span>
          }
        />
        <StatCard
          label="Safety Floor"
          value={formatINR(userFinancialProfile.safetyFloor)}
          subtitle="Protected 60-day living expense & EMI floor"
          icon={Shield}
          accentColor="var(--color-caution)"
          badge="Guaranteed"
          trend={
            <span className="text-[var(--text-secondary)] flex items-center gap-0.5 font-medium">
              Unbreached for 180+ days
            </span>
          }
        />
        <StatCard
          label="Available to Spend"
          value={formatINR(userFinancialProfile.availableToSpend)}
          subtitle="Liquid surplus above safety threshold"
          icon={CreditCard}
          accentColor="var(--color-safe)"
          trend={
            <span className="text-[var(--color-safe)] flex items-center gap-0.5 font-bold">
              Ready for allocation
            </span>
          }
        />
      </div>

      {/* Mini 90-day trend chart in INR */}
      <div className="glass-card rounded-3xl p-5 sm:p-6 border border-[var(--border-color)] theme-transition shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="font-headline text-lg sm:text-xl font-normal text-[var(--text-primary)]">
              90-Day Projected Cash Trend (INR)
            </h3>
            <p className="text-scale-caption text-[var(--text-secondary)]">
              Simulated baseline balance progression across upcoming payroll cycles
            </p>
          </div>
          <span className="text-scale-caption font-bold text-[var(--color-gold)]">
            High: ₹19,23,000
          </span>
        </div>

        <div style={{ height: '160px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecastPoints} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="dashboardTrendRoyalGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={primaryColor} stopOpacity={0.24} />
                  <stop offset="100%" stopColor={primaryColor} stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                stroke={axisColor}
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 10, fill: axisColor }}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="glass-card rounded-xl p-2.5 border border-[var(--border-color)] text-xs shadow-lg">
                        <span className="text-[var(--text-muted)] block font-medium">{data.date}</span>
                        <span className="font-bold text-[var(--color-primary)]">
                          {formatINR(data.balance)}
                        </span>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                type="monotone"
                dataKey="balance"
                stroke={primaryColor}
                strokeWidth={2.5}
                fill="url(#dashboardTrendRoyalGradient)"
                isAnimationActive={true}
                animationDuration={900}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Two columns: Active Payment Plans & Upcoming Events Timeline */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Active Payment Plans in INR */}
        <div className="glass-card rounded-3xl p-6 border border-[var(--border-color)] theme-transition flex flex-col justify-between shadow-lg">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-[var(--color-primary)]/15 text-[var(--color-primary)] flex items-center justify-center">
                  <Layers className="w-4 h-4" />
                </div>
                <h3 className="font-headline text-xl font-normal text-[var(--text-primary)]">
                  Active Payment Plans
                </h3>
              </div>
              <span className="text-scale-caption text-[var(--text-secondary)] font-bold">
                {activePlans.length} active
              </span>
            </div>

            <div className="space-y-4">
              {activePlans.map((plan) => (
                <div
                  key={plan.id}
                  className="p-4 rounded-2xl bg-[var(--bg-card-subtle)] border border-[var(--border-subtle)] space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <h4 className="text-scale-body font-medium text-[var(--text-primary)]">
                      {plan.title}
                    </h4>
                    <span className="text-scale-caption font-bold text-[var(--color-gold)]">
                      {formatINR(plan.paidAmount)} / {formatINR(plan.totalAmount)}
                    </span>
                  </div>

                  {/* Animated Progress Bar */}
                  <div className="w-full h-2 bg-[var(--bg-card)] rounded-full overflow-hidden border border-[var(--border-subtle)]">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${plan.progress}%` }}
                      transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
                      className="h-full bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-gold)] rounded-full"
                    />
                  </div>

                  <div className="flex items-center justify-between text-scale-caption text-[var(--text-secondary)] font-medium">
                    <span>
                      {plan.paidInstallments} of {plan.totalInstallments} payments made
                    </span>
                    <span className="font-semibold text-[var(--text-primary)]">
                      Next: {plan.nextDue}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[var(--border-subtle)]">
            <button
              onClick={onNavigateToPlan}
              className="w-full py-3 rounded-2xl border border-[var(--border-color)] hover:border-[var(--color-primary)] text-scale-label font-bold text-[var(--text-primary)] flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
            >
              <span>Manage Payment Schedule in Result</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Upcoming Events Timeline in INR */}
        <div className="glass-card rounded-3xl p-6 border border-[var(--border-color)] theme-transition shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-[var(--color-safe)]/15 text-[var(--color-safe)] flex items-center justify-center">
                <Calendar className="w-4 h-4" />
              </div>
              <h3 className="font-headline text-xl font-normal text-[var(--text-primary)]">
                Upcoming Cash Events (INR)
              </h3>
            </div>
            <span className="text-scale-caption text-[var(--text-secondary)] font-bold">
              Next 90 days
            </span>
          </div>

          <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
            {upcomingEvents.map((event) => (
              <div
                key={event.id}
                className="p-3.5 rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] flex items-center justify-between gap-3 text-scale-label"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-scale-caption font-bold text-[var(--text-muted)] w-14 shrink-0">
                    {event.date}
                  </span>
                  <div className="min-w-0 truncate">
                    <span className="text-[var(--text-primary)] font-semibold truncate block">
                      {event.label}
                    </span>
                    <span className="text-[10px] text-[var(--text-muted)] block font-medium">
                      {event.category}
                    </span>
                  </div>
                </div>

                <div className="text-right shrink-0">
                  <span
                    className={`font-bold ${
                      event.isIncome ? 'text-[var(--color-safe)]' : 'text-[var(--text-primary)]'
                    }`}
                  >
                    {event.isIncome ? `+${formatINR(event.amount)}` : `-${formatINR(Math.abs(event.amount))}`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default DashboardScreen;

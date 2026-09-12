/**
 * Buy or Wait? Theme, Currency & Motion Tokens
 * Royal Bright & Royal Sovereign Midnight Palettes
 */

export const colors = {
  light: {
    name: 'Royal Bright',
    background: '#FBF8F1',
    card: '#FFFFFF',
    cardSubtle: '#F5F0E4',
    foreground: '#0F172A',
    border: '#E2D8C6',
    borderSubtle: '#EDE5D5',
    primary: '#1D4ED8', // Imperial Sapphire
    gold: '#D97706',    // 24K Royal Gold
    safe: '#059669',    // Radiant Emerald
    caution: '#D97706', // Imperial Amber
    risk: '#DC2626',    // Royal Ruby
  },
  dark: {
    name: 'Royal Midnight',
    background: '#0A0E1A',
    card: '#131B2E',
    cardSubtle: '#1C2742',
    foreground: '#F8FAFC',
    border: '#283756',
    borderSubtle: '#1E2B45',
    primary: '#38BDF8', // Luminous Sapphire
    gold: '#FBBF24',    // Sovereign Gold
    safe: '#10B981',    // Luminous Emerald
    caution: '#F59E0B', // Luminous Amber
    risk: '#F43F5E',    // Vivid Ruby
  }
};

/**
 * Format Indian Rupee (INR / ₹) with standard Indian numbering (e.g. ₹2,80,000)
 */
export const formatINR = (val) => {
  if (val === null || val === undefined || isNaN(val)) return '₹0';
  const num = Math.round(Number(val));
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(num);
};

export const typography = {
  fontFamilies: {
    headline: "'DM Serif Display', Georgia, serif",
    body: "'Instrument Sans', -apple-system, BlinkMacSystemFont, sans-serif",
  },
  scale: {
    hero: '56px',
    display: '48px',
    stat: '30px',
    body: '15px',
    label: '13px',
    caption: '10px',
  }
};

export const motionTokens = {
  spring: {
    type: 'spring',
    stiffness: 300,
    damping: 28,
  },
  springBouncy: {
    type: 'spring',
    stiffness: 400,
    damping: 22,
  },
  screenTransition: {
    duration: 0.22,
    ease: [0.4, 0, 0.2, 1],
  },
  verdictEntrance: {
    duration: 0.38,
    ease: [0.22, 1, 0.36, 1],
  },
  staggerContainer: {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
      },
    },
  },
  staggerItem: {
    hidden: { opacity: 0, y: 14 },
    show: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 28,
      },
    },
  },
};

export const verdictMap = {
  affordable_now: {
    key: 'affordable_now',
    label: 'Affordable Now',
    badge: 'Safe to buy',
    colorVar: 'var(--color-safe)',
    lightHex: colors.light.safe,
    darkHex: colors.dark.safe,
    headline: 'You can comfortably afford this right now.',
    summary: 'Paying in full preserves your ₹8,00,000 safety floor and maintains a positive cash-flow buffer throughout the next 90 days.',
  },
  affordable_with_plan: {
    key: 'affordable_with_plan',
    label: 'Affordable with Plan',
    badge: 'Recommended',
    colorVar: 'var(--color-primary)',
    lightHex: colors.light.primary,
    darkHex: colors.dark.primary,
    headline: 'Affordable across 6 scheduled payments.',
    summary: 'A structured payment plan preserves your ₹8,00,000 cash reserve while absorbing the full ₹2,80,000 cost safely over 90 days.',
  },
  affordable_later: {
    key: 'affordable_later',
    label: 'Affordable Later',
    badge: 'Wait advised',
    colorVar: 'var(--color-caution)',
    lightHex: colors.light.caution,
    darkHex: colors.dark.caution,
    headline: 'Wait until Nov 1 salary credit for optimal safety.',
    summary: 'Buying immediately brings your liquid buffer dangerously close to your safety floor. Waiting 4 weeks ensures total peace of mind.',
  },
  not_affordable: {
    key: 'not_affordable',
    label: 'Not Affordable',
    badge: 'High risk',
    colorVar: 'var(--color-risk)',
    lightHex: colors.light.risk,
    darkHex: colors.dark.risk,
    headline: 'This purchase breaches your ₹8,00,000 safety floor.',
    summary: 'With scheduled rent, SIP investments, and upcoming obligations, this purchase causes a liquidity deficit by day 42.',
  }
};

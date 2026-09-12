# "Buy or Wait?" · AI Financial Affordability Web App

An intelligent personal finance interface that evaluates affordability against a 90-day cash-flow forecast and recommends structured payment strategies.

---

## Tech Stack & Architecture

- **React 18** + **Vite 6**
- **Tailwind CSS v4** (`@tailwindcss/vite`)
- **framer-motion 11**: Stagger containers, spring physics, layout reflow, and exit animations
- **recharts**: 90-day cash-flow `AreaChart` with animated draw-on, reference lines, and interactive custom tooltips
- **Google Fonts**:
  - `DM Serif Display`: Headline verdicts (48px) and stat figures (30px)
  - `Instrument Sans`: UI text across 4 strict scale steps (48px display, 15px body, 13px labels, 10px captions)
- **Lucide React**: Clean lightweight icons

---

## Directory Structure

```
src/
  components/
    StatusPill.jsx            # Verdict pills with dynamic color-mix borders & backgrounds
    Nav.jsx                   # Frosted glass nav, layoutId indicator, theme toggle, avatar
    BottomNav.jsx             # Mobile bottom navigation bar with safe-area insets
    VerdictCard.jsx           # Hero verdict card with color glow & stats chips
    ForecastChart.jsx         # Recharts AreaChart with safety floor & payment date dots
    PaymentPlanCard.jsx       # Progress bar, interactive installment chips with drawer
    SpendingChangesCard.jsx   # Interactive paused/dismissed recurring expenses with live totals
    ExplanationAccordion.jsx  # Collapsible "Why this recommendation" with 4 stat tiles
    RequestListRow.jsx        # Reusable request item with hover x-shift
    StatCard.jsx              # Hoverable metric card with DM Serif figures
  screens/
    AskScreen.jsx             # Hero, typewriter placeholder, query input, recent requests
    AnalyzingScreen.jsx       # 3-step spring progress sequence, spinning conic orb
    ResultScreen.jsx          # Complete staggered analysis view with all cards & CTA
    DashboardScreen.jsx       # Metrics, active plans, upcoming events, mini chart
    HistoryScreen.jsx         # Status/category filtered requests with popLayout transitions
  data/
    mockData.js               # Forecast points, payment plans, history, spending changes & API layer
  theme/
    ThemeProvider.jsx         # Theme context, CSS custom properties, 220ms crossfade
    tokens.js                 # Color, type, and motion tokens
  App.jsx
  main.jsx
```

---

## Theme System

Two dedicated themes with smooth 220ms CSS variable crossfading:
- **Light**: Background `#F7F6F2`, Card `#FFFFFF`, Text `#17181D`, Border `#E0DDD6`
- **Mid-dark**: Background `#1D2330`, Card `#28303F`, Text `#DCDAD4`, Border `#353E50`

Shared semantic colors (Light / Mid-dark):
- **Primary Teal**: `#0A6E6E` / `#30BABA`
- **Safe Green**: `#147A50` / `#2CB87A`
- **Caution Amber**: `#B06A0A` / `#D09E28`
- **Risk Coral**: `#A83636` / `#C45454`

Ambient lighting is provided by fixed radial gradients (teal top-right, safe-green bottom-left) at ~8% opacity.

---

## How to Run

1. Open a terminal in `scratch/buy-or-wait`:
   ```bash
   cd C:\Users\jaswa\.gemini\antigravity\scratch\buy-or-wait
   ```
2. Install dependencies (already installed):
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Build for production:
   ```bash
   npm run build
   ```

---

## Future Backend API Integration

The file [`src/data/mockData.js`](file:///C:/Users/jaswa/.gemini/antigravity/scratch/buy-or-wait/src/data/mockData.js) exposes an `api` service object:
- `api.analyzeRequest(payload)`: Evaluates a user purchase query
- `api.getForecast()`: Retrieves 90-day cash flow points
- `api.getHistory()`: Loads previous evaluations
- `api.getDashboard()`: Returns user financial profile, active plans, and timeline events

To wire up the live HackerRank backend, simply replace the simulated delays and mock objects in `src/data/mockData.js` with your endpoint calls (`fetch('/api/analyze', ...)`). The component tree is completely decoupled and will consume the response without requiring structural rewrites.

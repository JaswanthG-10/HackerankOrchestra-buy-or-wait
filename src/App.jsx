import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ThemeProvider } from './theme/ThemeProvider';
import Nav from './components/Nav';
import BottomNav from './components/BottomNav';
import Intro3D from './components/Intro3D';
import AskScreen from './screens/AskScreen';
import AnalyzingScreen from './screens/AnalyzingScreen';
import ResultScreen from './screens/ResultScreen';
import DashboardScreen from './screens/DashboardScreen';
import HistoryScreen from './screens/HistoryScreen';
import { sampleRequest } from './data/mockData';
import { analyzeAffordabilityWithAI } from './services/aiService';

export function App() {
  const [showIntro, setShowIntro] = useState(true);
  const [currentScreen, setCurrentScreen] = useState('ask');
  const [requestData, setRequestData] = useState(sampleRequest);

  const isAnalyzing = currentScreen === 'analyzing';

  // Handler when user triggers Analyze on Ask screen
  const handleStartAnalysis = async (params) => {
    const parsedAmount = Number(params.amount) || 280000;
    
    // Set preliminary request state for immediate feedback
    const pendingRequest = {
      ...sampleRequest,
      id: `req-${Date.now().toString().slice(-4)}`,
      title: params.query || 'Custom Purchase Evaluation',
      amount: parsedAmount,
      category: params.category || 'Purchase',
    };
    setRequestData(pendingRequest);
    setCurrentScreen('analyzing');

    // Run AI Evaluation in parallel with analyzing screen
    try {
      const aiEvaluation = await analyzeAffordabilityWithAI(
        params.query || 'Purchase Evaluation',
        parsedAmount,
        params.category || 'Purchase'
      );
      setRequestData(aiEvaluation);
    } catch (err) {
      console.warn('AI analysis error, using baseline model:', err);
    }
  };

  // Handler when analyzing screen finishes
  const handleAnalysisComplete = () => {
    setCurrentScreen('result');
  };

  // Handler when user picks a past history item
  const handleSelectHistoryItem = (item) => {
    const populatedReq = {
      ...sampleRequest,
      id: item.id,
      title: item.title,
      emoji: item.emoji,
      amount: item.amount,
      category: item.category,
      verdict: item.verdict,
      date: item.date,
      summary: item.notes || sampleRequest.summary,
      stats: {
        ...sampleRequest.stats,
        totalCost: item.amount,
        safeToPayNow: Math.min(60000, Math.round(item.amount / 4)),
      }
    };
    setRequestData(populatedReq);
    setCurrentScreen('result');
  };

  return (
    <ThemeProvider>
      {/* 3D Intro Experience */}
      <AnimatePresence>
        {showIntro && (
          <Intro3D onEnter={() => setShowIntro(false)} />
        )}
      </AnimatePresence>

      <div className="min-h-screen bg-[var(--bg-app)] text-[var(--text-primary)] relative theme-transition selection:bg-[var(--color-gold)] selection:text-[#0B101D]">
        {/* Multi-layered ambient royal radiance */}
        <div className="ambient-bg" />

        {/* Top frosted glass Nav */}
        <Nav
          currentScreen={currentScreen}
          setScreen={setCurrentScreen}
          isAnalyzing={isAnalyzing}
          onShowIntro={() => setShowIntro(true)}
        />

        {/* Main Content Area with Screen Transitions */}
        <main className="relative z-10">
          <AnimatePresence mode="wait">
            {currentScreen === 'ask' && (
              <AskScreen
                key="ask"
                onStartAnalysis={handleStartAnalysis}
                onSelectHistoryItem={handleSelectHistoryItem}
              />
            )}

            {currentScreen === 'analyzing' && (
              <AnalyzingScreen
                key="analyzing"
                requestData={requestData}
                onComplete={handleAnalysisComplete}
              />
            )}

            {currentScreen === 'result' && (
              <ResultScreen
                key="result"
                currentRequest={requestData}
                onBackToAsk={() => setCurrentScreen('ask')}
                onOpenOverview={() => setCurrentScreen('dashboard')}
              />
            )}

            {currentScreen === 'dashboard' && (
              <DashboardScreen
                key="dashboard"
                onNavigateToPlan={() => setCurrentScreen('result')}
              />
            )}

            {currentScreen === 'history' && (
              <HistoryScreen
                key="history"
                onSelectItem={handleSelectHistoryItem}
              />
            )}
          </AnimatePresence>
        </main>

        {/* Mobile Bottom Navigation */}
        <BottomNav
          currentScreen={currentScreen}
          setScreen={setCurrentScreen}
          isAnalyzing={isAnalyzing}
        />
      </div>
    </ThemeProvider>
  );
}

export default App;

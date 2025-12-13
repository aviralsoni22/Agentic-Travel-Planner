import React, { useState } from 'react';
import { TripPlan, TripRequest } from './types';
import { Home } from './components/Home';
import { PlannerForm } from './components/PlannerForm';
import { Dashboard } from './components/Dashboard';
import { generateItinerary } from './services/api'; // Use the real API

type ViewState = 'home' | 'form' | 'dashboard' | 'loading';

const App: React.FC = () => {
  const [view, setView] = useState<ViewState>('home');
  const [data, setData] = useState<TripPlan | null>(null);

  const handleStartPlanning = () => {
    setView('form');
  };

  const handleCancelPlanning = () => {
    setView('home');
  };
  
  const handleSubmitPlan = async (requestData: TripRequest) => {
    setView('loading');

    try {
      // 1. Get the raw response from the backend
      // We cast to 'any' because the wrapper structure differs from TripPlan
      const response: any = await generateItinerary(requestData);
      
      console.log("Full API Response:", response); // Helpful for debugging

      // 2. CHECK & UNWRAP: Is the data inside a 'plan' property?
      if (response && response.plan) {
          setData(response.plan); // ✅ Correct: Extract the inner plan
      } else {
          setData(response); // Fallback
      }

      setView('dashboard');
    } catch (error) {
      console.error("Planning failed:", error);
      alert("Failed to generate plan. Please try again.");
      setView('form'); 
    }
  };

  if (view === 'loading') {
    return (
      <div className="min-h-screen bg-[#003b95] flex flex-col items-center justify-center text-white">
        <div className="w-16 h-16 border-4 border-white/20 border-t-[#febb02] rounded-full animate-spin mb-8"></div>
        <h2 className="text-3xl font-bold mb-3 tracking-tight">Booking.ai</h2>
        <p className="opacity-80 font-medium">Curating your perfect itinerary...</p>
        <p className="text-sm opacity-60 mt-2">Agents are researching (this takes ~2 mins)...</p>
      </div>
    );
  }

  if (view === 'dashboard' && data) {
    return <Dashboard data={data} />;
  }

  return (
    <>
      <Home onStartPlanning={handleStartPlanning} />
      {view === 'form' && (
        <PlannerForm
          onCancel={handleCancelPlanning}
          onSubmit={handleSubmitPlan}
        />
      )}
    </>
  );
};

export default App;
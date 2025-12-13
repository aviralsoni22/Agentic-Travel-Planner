import React, { createContext, useContext, useState, ReactNode } from 'react';
import { TripPlan, TripRequest } from '../types';
import { MOCK_TRIP_DATA } from '../constants';
import { fetchTripPlan } from '../services/api';

type ViewState = 'home' | 'form' | 'dashboard' | 'loading';

interface TripContextType {
  view: ViewState;
  data: TripPlan | null;
  loadingMessage: string;
  startPlanning: () => void;
  cancelPlanning: () => void;
  submitPlan: (requestData: TripRequest) => Promise<void>;
}

const TripContext = createContext<TripContextType | undefined>(undefined);

export const TripProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [view, setView] = useState<ViewState>('home');
  const [data, setData] = useState<TripPlan | null>(null);
  const [loadingMessage, setLoadingMessage] = useState("Initializing Agents...");

  const startPlanning = () => {
    setView('form');
  };

  const cancelPlanning = () => {
    setView('home');
  };

  const submitPlan = async (requestData: TripRequest) => {
    setView('loading');
    
    const messages = [
        "Analyzing destination constraints...",
        "Agents searching for flights...", 
        "Checking hotel availability...",
        "Curating local experiences...",
        "Optimizing budget allocation...",
        "Finalizing itinerary..."
    ];
    let msgIndex = 0;
    setLoadingMessage(messages[0]);
    
    const intervalId = setInterval(() => {
        msgIndex = (msgIndex + 1) % messages.length;
        setLoadingMessage(messages[msgIndex]);
    }, 3000);

    try {
        const planData = await fetchTripPlan(requestData);
        
        clearInterval(intervalId);
        setData(planData);
        setView('dashboard');

    } catch (error) {
        clearInterval(intervalId);
        console.error("Failed to fetch trip plan:", error);
        
        // Graceful fallback logic
        const useMock = window.confirm(
            "Could not connect to the Agentic Backend at http://localhost:8000/plan.\n\n" + 
            "Make sure your CrewAI server is running.\n\n" + 
            "Would you like to generate a demo plan instead?"
        );

        if (useMock) {
             const updatedData = {
                ...MOCK_TRIP_DATA,
                destination: requestData.destination || MOCK_TRIP_DATA.destination,
                start_date: requestData.startDate,
                end_date: requestData.endDate,
                num_travelers: requestData.travelers,
                trip_duration: requestData.duration,
                group_category: requestData.groupType,
                interests: requestData.interests.split(',').map(i => i.trim()),
            };
            setData(updatedData);
            setView('dashboard');
        } else {
            setView('form');
        }
    }
  };

  return (
    <TripContext.Provider value={{ 
      view, 
      data, 
      loadingMessage, 
      startPlanning, 
      cancelPlanning, 
      submitPlan 
    }}>
      {children}
    </TripContext.Provider>
  );
};

export const useTrip = () => {
  const context = useContext(TripContext);
  if (context === undefined) {
    throw new Error('useTrip must be used within a TripProvider');
  }
  return context;
};
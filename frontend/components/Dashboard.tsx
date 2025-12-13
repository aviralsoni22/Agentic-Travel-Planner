import React, { useState } from 'react';
import { TripPlan } from '../types';
import { Hero } from './Hero';
import { BudgetSidebar } from './BudgetSidebar';
import { TripPulse } from './TripPulse';
import { BookingDetails } from './BookingDetails';
import { ItineraryList } from './ItineraryList';
import { Footer } from './Footer';
import { ChatWidget } from './ChatWidget';
import { Navbar } from './Navbar';
import { Insights } from './Insights';

interface DashboardProps {
  data: TripPlan;
}

export const Dashboard: React.FC<DashboardProps> = ({ data }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-[#f5f7fa] font-sans antialiased">
      <Navbar />

      {/* Hero Section */}
      <Hero data={data} />

      {/* Main Content Grid with Negative Margin Overlap */}
      <main className="flex-grow max-w-7xl mx-auto w-full px-4 md:px-8 -mt-20 relative z-20">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Details & Itinerary */}
          <div className="lg:col-span-2 space-y-8">
             <TripPulse data={data} />
             <Insights data={data} />
             <BookingDetails data={data} />
             <ItineraryList data={data} />
          </div>

          {/* Right Column: Sticky Budget & Actions */}
          <div className="lg:col-span-1">
             <BudgetSidebar data={data} onOpenChat={() => setIsChatOpen(true)} />
          </div>

        </div>
      </main>

      {/* Chat Widget */}
      <ChatWidget isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} tripData={data} />

      <Footer />
    </div>
  );
};
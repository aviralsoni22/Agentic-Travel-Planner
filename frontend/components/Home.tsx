
import React from 'react';
import { Navbar } from './Navbar';
import { Footer } from './Footer';
import { BedDouble, Plane, Car, Sparkles, Calendar, User, Search } from 'lucide-react';

interface HomeProps {
  onStartPlanning: () => void;
}

export const Home: React.FC<HomeProps> = ({ onStartPlanning }) => {
  return (
    <div className="min-h-screen bg-[#f5f7fa] font-sans flex flex-col">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-booking-blue text-white pb-20 pt-8 px-4 md:px-8 relative overflow-hidden">
        <div className="max-w-7xl mx-auto relative z-10">
          <h1 className="text-5xl font-extrabold mb-4 tracking-tight leading-tight">
            Find your next stay
          </h1>
          <p className="text-2xl font-light mb-12 opacity-90">
            Search deals on hotels, homes, and much more...
          </p>

          {/* Search Bar Visual */}
          <div className="bg-booking-yellow p-1 rounded-lg max-w-5xl shadow-xl flex flex-col md:flex-row gap-1">
            <div className="flex-1 bg-white rounded-md flex items-center px-4 py-3 text-gray-700 gap-3 border border-transparent focus-within:border-booking-blue hover:bg-gray-50 transition-colors cursor-text">
                <BedDouble className="text-gray-400" />
                <span className="text-sm font-medium">Where are you going?</span>
            </div>
            <div className="flex-1 bg-white rounded-md flex items-center px-4 py-3 text-gray-700 gap-3 hover:bg-gray-50 transition-colors cursor-pointer">
                <Calendar className="text-gray-400" />
                <span className="text-sm font-medium">Check-in Date — Check-out Date</span>
            </div>
            <div className="flex-1 bg-white rounded-md flex items-center px-4 py-3 text-gray-700 gap-3 hover:bg-gray-50 transition-colors cursor-pointer">
                <User className="text-gray-400" />
                <span className="text-sm font-medium">2 adults · 0 children · 1 room</span>
            </div>
            <button className="bg-booking-blue text-white px-8 py-3 rounded-md font-bold text-lg hover:bg-blue-800 transition-colors">
                Search
            </button>
          </div>
        </div>
      </div>

      {/* Feature Section: Agentic Planner */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 -mt-10 relative z-20 w-full mb-16">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-booking-yellow/10 rounded-full -mr-16 -mt-16 blur-3xl"></div>
            
            <div className="relative z-10 flex-1">
                <div className="inline-flex items-center gap-2 bg-blue-50 text-booking-blue px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4 border border-blue-100">
                    <Sparkles size={14} />
                    New Feature
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-3">
                    Agentic Travel Planner
                </h2>
                <p className="text-gray-600 text-lg leading-relaxed mb-6 max-w-xl">
                    Experience the future of travel. Tell our AI agent your interests, budget, and dreams, and watch it craft a complete itinerary with real-time reasoning and pricing.
                </p>
                <button 
                    onClick={onStartPlanning}
                    className="bg-booking-blue text-white text-lg font-bold py-3 px-8 rounded-lg hover:bg-blue-800 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 flex items-center gap-2"
                >
                    <Sparkles size={20} className="text-booking-yellow" />
                    Start Planning Now
                </button>
            </div>

            <div className="relative w-full md:w-1/3 aspect-video bg-gray-100 rounded-xl overflow-hidden shadow-inner border border-gray-200 group cursor-pointer" onClick={onStartPlanning}>
                <img 
                    src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=1000&auto=format&fit=crop" 
                    alt="Travel Planning" 
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/40">
                         <Sparkles className="text-white" />
                    </div>
                </div>
            </div>
        </div>
      </div>

      {/* Offers Section */}
      <div className="max-w-7xl mx-auto px-4 md:px-8 w-full mb-12">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Offers</h3>
        <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex items-center gap-6 relative overflow-hidden">
                <div className="flex-1 relative z-10">
                    <h4 className="font-bold text-lg mb-2">Fly away to your dream holiday</h4>
                    <p className="text-gray-600 text-sm mb-4">Get 15% off flights worldwide.</p>
                    <button className="bg-booking-blue text-white text-sm font-bold px-4 py-2 rounded hover:bg-blue-800">Book Flight</button>
                </div>
                <div className="w-32 h-32 relative">
                     <div className="absolute inset-0 bg-blue-100 rounded-full opacity-50"></div>
                     <Plane className="absolute inset-0 m-auto text-booking-blue w-16 h-16" />
                </div>
            </div>
             <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex items-center gap-6 relative overflow-hidden">
                <div className="flex-1 relative z-10">
                    <h4 className="font-bold text-lg mb-2">Take your longest holiday yet</h4>
                    <p className="text-gray-600 text-sm mb-4">Browse properties for long-term stays.</p>
                    <button className="bg-booking-blue text-white text-sm font-bold px-4 py-2 rounded hover:bg-blue-800">Find Stays</button>
                </div>
                <div className="w-32 h-32 relative">
                     <div className="absolute inset-0 bg-orange-100 rounded-full opacity-50"></div>
                     <Car className="absolute inset-0 m-auto text-orange-500 w-16 h-16" />
                </div>
            </div>
        </div>
      </div>

      <div className="mt-auto">
        <Footer />
      </div>
    </div>
  );
};

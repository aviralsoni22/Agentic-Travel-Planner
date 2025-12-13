import React, { useState, useEffect, useRef } from 'react';
import { X, Sparkles, Calendar, Users, ArrowRight, MapPin, Wallet, Hash, ChevronDown, ChevronUp } from 'lucide-react';
import { TripRequest } from '../types';

interface PlannerFormProps {
  onCancel: () => void;
  onSubmit: (data: TripRequest) => void;
}

export const PlannerForm: React.FC<PlannerFormProps> = ({ onCancel, onSubmit }) => {
  const [formData, setFormData] = useState<TripRequest>({
    origin: 'New Delhi, India',
    destination: 'Panaji, Goa, India',
    startDate: '2026-01-10',
    endDate: '2026-01-13',
    budget: 1500,
    duration: 3,
    groupType: 'Couple',
    travelers: 2,
    interests: 'Beaches, Food, Nightlife'
  });

  const startDateRef = useRef<HTMLInputElement>(null);
  const endDateRef = useRef<HTMLInputElement>(null);

  // Helper to trigger date picker
  const showPicker = (ref: React.RefObject<HTMLInputElement>) => {
    try {
      if (ref.current && 'showPicker' in ref.current) {
        (ref.current as any).showPicker();
      } else {
        ref.current?.focus();
      }
    } catch (e) {
      console.error("Error opening picker:", e);
      // Fallback to focus if showPicker fails (e.g., transient user activation issues)
      ref.current?.focus();
    }
  };

  // Helper to parse "YYYY-MM-DD" as local date at midnight to avoid timezone shifts
  const parseLocalDate = (dateStr: string): Date | null => {
      if (!dateStr) return null;
      const [y, m, d] = dateStr.split('-').map(Number);
      return new Date(y, m - 1, d);
  };

  // Effect to calculate duration when dates change
  useEffect(() => {
    const start = parseLocalDate(formData.startDate);
    const end = parseLocalDate(formData.endDate);
    
    if (start && end) {
        const diffTime = end.getTime() - start.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        // Only update if duration is different and valid
        if (diffDays >= 0 && diffDays !== formData.duration) {
            setFormData(prev => ({ ...prev, duration: diffDays }));
        }
    }
  }, [formData.startDate, formData.endDate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => {
        const newData = { ...prev, [name]: value };

        // Logic: Ensure End Date >= Start Date
        if (name === 'startDate') {
             if (newData.endDate < value) {
                 newData.endDate = value; // Reset end to start if start moves past it
             }
        }
        
        if (name === 'endDate') {
             if (newData.startDate > value) {
                 newData.startDate = value; // Reset start to end if end moves before it
             }
        }

        return newData;
    });
  };

  const adjustNumber = (field: keyof TripRequest, amount: number, min: number) => {
    setFormData(prev => {
        const currentVal = Number(prev[field]);
        const newVal = Math.max(min, currentVal + amount);
        return { ...prev, [field]: newVal };
    });
  };
  
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
        <div className="bg-white w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300 flex flex-col max-h-[90vh]">
            {/* Header */}
            <div className="bg-booking-blue p-6 flex justify-between items-center text-white shrink-0">
                <div className="flex items-center gap-4">
                    <div className="bg-booking-yellow p-2.5 rounded-xl text-booking-blue shadow-lg">
                         <Sparkles size={24} fill="currentColor" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold leading-tight">Agentic Trip Planner</h2>
                        <p className="text-blue-200 text-xs font-medium">AI-powered itinerary customization</p>
                    </div>
                </div>
                <button onClick={onCancel} className="bg-white/10 hover:bg-white/20 p-2 rounded-full transition-colors">
                    <X size={20} />
                </button>
            </div>

            {/* Scrollable Form Body */}
            <div className="p-8 overflow-y-auto custom-scrollbar">
                
                {/* 1. Destination Section */}
                <section className="mb-10">
                    <h3 className="text-gray-900 font-bold text-lg mb-5 flex items-center gap-2.5">
                        <MapPin className="text-booking-blue" size={22} />
                        Where to?
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-[1fr,auto,1fr] gap-4 items-end">
                        <div className="w-full">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">Origin</label>
                            <div className="relative group">
                                <MapPin className="absolute left-4 top-3.5 text-gray-400 group-focus-within:text-booking-blue transition-colors" size={20} />
                                <input 
                                    type="text"
                                    name="origin"
                                    value={formData.origin}
                                    onChange={handleChange}
                                    required
                                    className="w-full bg-gray-50 text-gray-900 pl-12 p-3.5 rounded-xl font-semibold border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all placeholder-gray-400"
                                    placeholder="From where?"
                                />
                            </div>
                        </div>
                        
                        <div className="hidden md:flex items-center justify-center pb-4 text-gray-300">
                            <ArrowRight size={24} />
                        </div>

                        <div className="w-full">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">Destination</label>
                            <div className="relative group">
                                <MapPin className="absolute left-4 top-3.5 text-gray-400 group-focus-within:text-booking-blue transition-colors" size={20} />
                                <input 
                                    type="text"
                                    name="destination"
                                    value={formData.destination}
                                    onChange={handleChange}
                                    required
                                    className="w-full bg-gray-50 text-gray-900 pl-12 p-3.5 rounded-xl font-semibold border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all placeholder-gray-400"
                                    placeholder="To where?"
                                />
                            </div>
                        </div>
                    </div>
                </section>

                <div className="w-full h-px bg-gray-100 mb-10"></div>

                {/* 2. Dates & Budget Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10 mb-10">
                    
                    {/* Dates */}
                    <section>
                         <h3 className="text-gray-900 font-bold text-lg mb-5 flex items-center gap-2.5">
                            <Calendar className="text-booking-blue" size={22} />
                            When?
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">Start</label>
                                <div 
                                    className="relative group cursor-pointer" 
                                    onClick={() => showPicker(startDateRef)}
                                >
                                     <div className="absolute left-4 top-3.5 pointer-events-none z-10">
                                        <Calendar size={18} className="text-gray-400 group-focus-within:text-booking-blue transition-colors" />
                                     </div>
                                    <input 
                                        ref={startDateRef}
                                        type="date"
                                        name="startDate"
                                        min={today}
                                        value={formData.startDate}
                                        onChange={handleChange}
                                        required
                                        onClick={() => showPicker(startDateRef)}
                                        className="w-full bg-gray-50 text-gray-900 pl-12 pr-10 p-3.5 rounded-xl font-semibold border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all relative cursor-pointer [&::-webkit-calendar-picker-indicator]:opacity-0 [&::-webkit-calendar-picker-indicator]:absolute [&::-webkit-calendar-picker-indicator]:w-full"
                                    />
                                    <div className="absolute right-4 top-3.5 pointer-events-none z-10">
                                        <ChevronDown size={18} className="text-gray-400 group-focus-within:text-booking-blue transition-colors" />
                                    </div>
                                </div>
                            </div>
                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">End</label>
                                <div 
                                    className="relative group cursor-pointer"
                                    onClick={() => showPicker(endDateRef)}
                                >
                                     <div className="absolute left-4 top-3.5 pointer-events-none z-10">
                                        <Calendar size={18} className="text-gray-400 group-focus-within:text-booking-blue transition-colors" />
                                     </div>
                                    <input 
                                        ref={endDateRef}
                                        type="date"
                                        name="endDate"
                                        min={formData.startDate || today}
                                        value={formData.endDate}
                                        onChange={handleChange}
                                        required
                                        onClick={() => showPicker(endDateRef)}
                                        className="w-full bg-gray-50 text-gray-900 pl-12 pr-10 p-3.5 rounded-xl font-semibold border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all relative cursor-pointer [&::-webkit-calendar-picker-indicator]:opacity-0 [&::-webkit-calendar-picker-indicator]:absolute [&::-webkit-calendar-picker-indicator]:w-full"
                                    />
                                    <div className="absolute right-4 top-3.5 pointer-events-none z-10">
                                        <ChevronDown size={18} className="text-gray-400 group-focus-within:text-booking-blue transition-colors" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Budget */}
                    <section>
                        <h3 className="text-gray-900 font-bold text-lg mb-5 flex items-center gap-2.5">
                            <Wallet className="text-booking-blue" size={22} />
                            Budget
                        </h3>
                        <div className="w-full relative group">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">Total Budget</label>
                            <div className="relative">
                                <span className="absolute left-4 top-3.5 text-gray-400 font-bold group-focus-within:text-booking-blue text-lg">$</span>
                                <input 
                                    type="number"
                                    name="budget"
                                    min={0}
                                    value={formData.budget}
                                    onChange={handleChange}
                                    required
                                    className="w-full bg-gray-50 text-gray-900 pl-9 pr-24 p-3.5 rounded-xl font-bold text-lg border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all appearance-none"
                                />
                                <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-3">
                                    <span className="text-gray-400 text-xs font-bold">USD</span>
                                    <div className="flex flex-col gap-0.5">
                                        <button 
                                            type="button" 
                                            onClick={() => adjustNumber('budget', 50, 0)}
                                            className="text-gray-400 hover:text-booking-blue hover:bg-blue-50 rounded p-0.5 transition-colors"
                                        >
                                            <ChevronUp size={14} strokeWidth={3} />
                                        </button>
                                        <button 
                                            type="button" 
                                            onClick={() => adjustNumber('budget', -50, 0)}
                                            className="text-gray-400 hover:text-booking-blue hover:bg-blue-50 rounded p-0.5 transition-colors"
                                        >
                                            <ChevronDown size={14} strokeWidth={3} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                </div>

                <div className="w-full h-px bg-gray-100 mb-10"></div>

                {/* 3. Details & Interests */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-10">
                    <section>
                         <h3 className="text-gray-900 font-bold text-lg mb-5 flex items-center gap-2.5">
                            <Users className="text-booking-blue" size={22} />
                            Who?
                        </h3>
                        <div className="flex gap-4">
                            <div className="flex-1">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">Group Type</label>
                                <div className="relative">
                                    <select 
                                        name="groupType"
                                        value={formData.groupType}
                                        onChange={handleChange}
                                        className="w-full bg-gray-50 text-gray-900 px-4 py-3.5 rounded-xl font-semibold border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all appearance-none cursor-pointer"
                                    >
                                        <option>Couple</option>
                                        <option>Family</option>
                                        <option>Friends</option>
                                        <option>Solo</option>
                                        <option>Business</option>
                                    </select>
                                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                                        <ArrowRight size={16} className="rotate-90" />
                                    </div>
                                </div>
                            </div>
                            <div className="w-36">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">Travelers</label>
                                <div className="relative">
                                    <input 
                                        type="number"
                                        name="travelers"
                                        min={1}
                                        value={formData.travelers}
                                        onChange={handleChange}
                                        required
                                        className="w-full bg-gray-50 text-gray-900 pl-4 pr-10 p-3.5 rounded-xl font-bold text-lg border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all text-center appearance-none"
                                    />
                                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex flex-col gap-0.5">
                                        <button 
                                            type="button" 
                                            onClick={() => adjustNumber('travelers', 1, 1)}
                                            className="text-gray-400 hover:text-booking-blue hover:bg-blue-50 rounded p-0.5 transition-colors"
                                        >
                                            <ChevronUp size={14} strokeWidth={3} />
                                        </button>
                                        <button 
                                            type="button" 
                                            onClick={() => adjustNumber('travelers', -1, 1)}
                                            className="text-gray-400 hover:text-booking-blue hover:bg-blue-50 rounded p-0.5 transition-colors"
                                        >
                                            <ChevronDown size={14} strokeWidth={3} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section className="flex flex-col">
                        <h3 className="text-gray-900 font-bold text-lg mb-5 flex items-center gap-2.5">
                            <Sparkles className="text-booking-blue" size={22} />
                            Vibe?
                        </h3>
                        <div className="flex-1">
                            <label className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 block ml-1">Interests (Keywords)</label>
                            <div className="relative h-full">
                                <div className="absolute left-4 top-4 text-gray-400">
                                    <Hash size={18} />
                                </div>
                                <input 
                                    name="interests"
                                    value={formData.interests}
                                    onChange={handleChange}
                                    required
                                    placeholder="e.g. Beaches, Food, Nightlife"
                                    className="w-full bg-gray-50 text-gray-900 pl-11 pr-4 py-3.5 rounded-xl font-semibold border border-gray-200 focus:bg-white focus:border-booking-blue focus:ring-4 focus:ring-blue-50/50 outline-none transition-all"
                                />
                            </div>
                        </div>
                    </section>
                </div>
            </div>

            {/* Footer Actions */}
            <div className="p-6 bg-gray-50 border-t border-gray-100 flex justify-end gap-4 shrink-0">
                <button 
                    onClick={onCancel}
                    className="px-6 py-3 font-bold text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-xl transition-colors"
                >
                    Cancel
                </button>
                <button 
                    onClick={() => onSubmit(formData)}
                    className="bg-booking-blue text-white font-bold px-8 py-3 rounded-xl hover:bg-blue-800 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 flex items-center gap-2.5"
                >
                    <Sparkles size={18} className="text-booking-yellow fill-booking-yellow" />
                    Create Plan
                </button>
            </div>
        </div>
    </div>
  );
};
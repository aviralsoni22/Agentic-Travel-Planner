import React from 'react';
import { TripPlan } from '../types';
import { Calendar, Users, Briefcase, Tag, Sparkles } from 'lucide-react';
import { formatDate } from '../utils/format';

interface HeroProps {
  data: TripPlan;
}

export const Hero: React.FC<HeroProps> = ({ data }) => {
  return (
    <div className="relative bg-booking-blue text-white overflow-hidden min-h-[400px] flex flex-col justify-center">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
            <img 
                src="https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=1920&auto=format&fit=crop" 
                alt="Destination" 
                className="w-full h-full object-cover opacity-30"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-booking-blue/90 via-booking-blue/60 to-booking-blue/95"></div>
        </div>

        <div className="max-w-7xl mx-auto w-full pt-8 pb-24 px-4 md:px-8 relative z-10">
            <div className="inline-flex items-center gap-2 mb-6 bg-booking-yellow/20 backdrop-blur-md border border-booking-yellow/40 text-booking-yellow px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm">
                <Sparkles size={14} />
                <span>AI-Curated Experience</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold mb-6 text-white tracking-tight drop-shadow-md">
                {data.destination}
            </h1>

            <div className="flex flex-wrap gap-3 mb-10">
                 <div className="flex items-center gap-2 bg-white/10 backdrop-blur-md px-4 py-2 rounded-full text-sm font-medium border border-white/20 hover:bg-white/20 transition-colors">
                    <Users size={16} className="text-booking-yellow" />
                    <span>{data.group_category} Trip</span>
                 </div>
                 {data.interests.map((interest, idx) => (
                     <div key={idx} className="flex items-center gap-2 bg-white/10 backdrop-blur-md px-4 py-2 rounded-full text-sm font-medium border border-white/20 hover:bg-white/20 transition-colors">
                        <Tag size={14} className="opacity-80"/>
                        <span className="capitalize">{interest}</span>
                     </div>
                 ))}
            </div>

            <div className="inline-grid grid-cols-1 md:grid-cols-3 gap-6 text-lg font-medium bg-white/5 backdrop-blur-md p-6 rounded-2xl border border-white/10">
                <div className="flex items-center gap-4">
                    <div className="p-2.5 bg-white/10 rounded-xl">
                        <Calendar className="text-booking-yellow" size={20} />
                    </div>
                    <div className="flex flex-col">
                        <span className="text-xs opacity-70 uppercase tracking-wider font-bold">Dates</span>
                        <span className="text-base font-semibold">{formatDate(data.start_date)} - {formatDate(data.end_date)}</span>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <div className="p-2.5 bg-white/10 rounded-xl">
                        <Briefcase className="text-booking-yellow" size={20} />
                    </div>
                     <div className="flex flex-col">
                        <span className="text-xs opacity-70 uppercase tracking-wider font-bold">Duration</span>
                        <span className="text-base font-semibold">{data.trip_duration} Days</span>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                     <div className="p-2.5 bg-white/10 rounded-xl">
                        <Users className="text-booking-yellow" size={20} />
                    </div>
                     <div className="flex flex-col">
                        <span className="text-xs opacity-70 uppercase tracking-wider font-bold">Travelers</span>
                        <span className="text-base font-semibold">{data.num_travelers} People</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
};
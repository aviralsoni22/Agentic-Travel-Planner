import React from 'react';
import { TripPlan } from '../types';
import { CheckCircle2, AlertOctagon, Activity, Hash, XCircle, Map, Sparkles } from 'lucide-react';

interface TripPulseProps {
    data: TripPlan;
}

export const TripPulse: React.FC<TripPulseProps> = ({ data }) => {
    // SAFEGUARD 1: If data itself is null, show loading or nothing.
    if (!data) return null;

    // SAFEGUARD 2: Create safe defaults for arrays to prevent "read property of null" errors.
    const itinerary = data.itinerary_by_day || [];
    const failures = data.failures || [];
    const interests = data.interests || [];

    const steps = [
        { label: 'Flights', status: data.flights ? 'success' : 'failed', detail: data.flights ? 'Booked' : 'Not Found' },
        { label: 'Hotel', status: data.hotel ? 'success' : 'failed', detail: data.hotel ? 'Reserved' : 'Unavailable' },
        {
            label: 'Itinerary',
            status: itinerary.length > 0 ? 'success' : 'pending',
            detail: `${itinerary.length} Days`
        },
    ];

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-0 mb-8 overflow-hidden">
            {/* Header Section */}
            <div className="bg-gradient-to-r from-gray-900 to-gray-800 p-6 text-white flex justify-between items-center relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Activity size={100} />
                </div>
                <div className="relative z-10">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <Sparkles className="text-booking-yellow" size={20} />
                        Trip Pulse
                    </h2>
                    <p className="text-gray-400 text-sm mt-1">Status of your agentic planning session</p>
                </div>

                <div className="relative z-10 text-right">
                    <div className="text-3xl font-bold text-booking-yellow">
                        {(() => {
                            if (!data.start_date || !data.end_date) return 1;
                            const start = new Date(data.start_date);
                            const end = new Date(data.end_date);
                            const diffTime = Math.abs(end.getTime() - start.getTime());
                            return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                        })()}
                    </div>
                    <div className="text-xs uppercase tracking-wider font-bold text-gray-400">Days</div>
                </div>
            </div>

            <div className="p-6">
                {/* Status Steps */}
                <div className="flex items-center justify-between mb-8 relative">
                    <div className="absolute top-4 left-0 w-full h-1 bg-gray-100 rounded-full -z-10"></div>

                    {steps.map((step, idx) => (
                        <div key={idx} className="flex flex-col items-center gap-2 bg-white px-2">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-colors duration-300
                            ${step.status === 'success' ? 'bg-green-50 border-green-500 text-green-600' :
                                    step.status === 'failed' ? 'bg-red-50 border-red-500 text-red-600' : 'bg-gray-50 border-gray-300 text-gray-400'}`}>
                                {step.status === 'success' ? <CheckCircle2 size={16} /> :
                                    step.status === 'failed' ? <XCircle size={16} /> : <Hash size={16} />}
                            </div>
                            <div className="text-center">
                                <div className="text-xs font-bold text-gray-900 uppercase tracking-wide">{step.label}</div>
                                <div className={`text-[10px] font-semibold ${step.status === 'failed' ? 'text-red-500' : 'text-gray-500'}`}>
                                    {step.detail}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Critical Alerts - Safely accessing the safe 'failures' variable */}
                {failures.length > 0 && (
                    <div className="mb-6 bg-red-50 border border-red-100 rounded-xl p-4 flex gap-4 animate-pulse-slow">
                        <div className="mt-0.5 text-red-600 shrink-0">
                            <AlertOctagon size={20} />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-red-900 mb-1">Critical Attention Needed</h4>
                            {failures.map((fail, i) => (
                                <p key={i} className="text-sm text-red-700 leading-snug">
                                    {fail.reason}
                                </p>
                            ))}
                            <button className="mt-3 text-xs bg-red-100 hover:bg-red-200 text-red-800 font-bold px-3 py-1.5 rounded-md transition-colors">
                                Resolve Budget Issue
                            </button>
                        </div>
                    </div>
                )}

                <div>
                    <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-1">
                        <Map size={14} /> Experience Vibe
                    </h4>
                    <div className="flex flex-wrap gap-2">
                        <span className="px-3 py-1 rounded-full bg-blue-50 text-booking-blue text-xs font-bold border border-blue-100 flex items-center gap-1.5">
                            <CheckCircle2 size={12} />
                            {data.group_category}
                        </span>
                        {interests.map((interest, idx) => {
                            // Check if this interest is actually covered in the itinerary
                            const isCovered = itinerary.some(day =>
                                day.activities.some(act =>
                                    (act.category?.toLowerCase().includes(interest.toLowerCase())) ||
                                    (act.name.toLowerCase().includes(interest.toLowerCase())) ||
                                    (act.description.toLowerCase().includes(interest.toLowerCase()))
                                ) ||
                                day.notes?.toLowerCase().includes(interest.toLowerCase())
                            );

                            return (
                                <span key={idx} className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 transition-colors cursor-default
                                    ${isCovered
                                        ? 'bg-blue-50 text-booking-blue border-blue-100'
                                        : 'bg-gray-50 text-gray-400 border-gray-100'}`}>
                                    {isCovered ? <CheckCircle2 size={10} /> : <Hash size={10} />}
                                    {interest}
                                </span>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};
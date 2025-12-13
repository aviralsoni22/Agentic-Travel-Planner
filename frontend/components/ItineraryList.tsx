import React from 'react';
import { TripPlan, Activity } from '../types';
import { CalendarDays, MapPin, Clock, Lightbulb } from 'lucide-react';
import { formatDate } from '../utils/format';

interface ItineraryListProps {
  data: TripPlan;
}

export const ItineraryList: React.FC<ItineraryListProps> = ({ data }) => {
  // SAFEGUARD: Default to empty array if itinerary is null
  const itinerary = data.itinerary_by_day || [];

  // If there is no itinerary yet, show a friendly message instead of a white screen
  if (itinerary.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        <h2 className="text-xl font-bold mb-2">Generating Itinerary...</h2>
        <p>The agents are still finalizing your daily plan.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3 border-b border-gray-200 pb-5">
        <div className="bg-booking-yellow/10 p-2 rounded-lg">
            <CalendarDays className="text-booking-yellow" size={24} />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Daily Itinerary</h2>
      </div>

      <div className="relative space-y-8 pl-4">
        {/* Continuous Line */}
        <div className="absolute left-[27px] top-2 bottom-0 w-[2px] bg-gray-200"></div>

        {/* FIX IS HERE: Use safe 'itinerary' variable */}
        {itinerary.map((dayPlan, index) => (
          <div key={index} className="relative pl-12 group">
            {/* Timeline Dot */}
            <div className="absolute left-[18px] top-1.5 w-5 h-5 rounded-full bg-white border-[4px] border-booking-blue z-10 shadow-sm group-hover:scale-110 group-hover:border-booking-yellow transition-all duration-300"></div>
            
            <div className="mb-6 flex items-baseline gap-3">
              <h3 className="text-xl font-bold text-gray-900">Day {index + 1}</h3>
              <span className="text-sm font-medium text-gray-500 bg-gray-100 px-3 py-1 rounded-full border border-gray-200">
                   {formatDate(dayPlan.day)}
              </span>
            </div>

            <div className="space-y-4">
                {/* Special Check-in logic */}
                {index === 0 && data.hotel && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-start gap-4 hover:shadow-sm transition-shadow">
                        <div className="bg-yellow-100 p-2 rounded-full text-yellow-700 shrink-0 mt-0.5">
                             <Lightbulb size={16} />
                        </div>
                        <div className="text-sm text-yellow-900">
                            <span className="block font-bold mb-0.5">Check-in required</span>
                            Proceed to <span className="font-semibold">{data.hotel.name}</span> after arrival.
                        </div>
                    </div>
                )}

                {dayPlan.activities.length === 0 ? (
                    <div className="border border-dashed border-gray-300 rounded-xl p-8 text-center bg-gray-50">
                        <p className="text-gray-400 font-medium italic">Free time scheduled for exploration.</p>
                    </div>
                ) : (
                    dayPlan.activities.map((activity, actIdx) => (
                        <ActivityCard key={actIdx} activity={activity} />
                    ))
                )}
                 
                 {/* Special Check-out logic */}
                 {index === itinerary.length - 1 && data.hotel && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-start gap-4 mt-4 hover:shadow-sm transition-shadow">
                        <div className="bg-yellow-100 p-2 rounded-full text-yellow-700 shrink-0 mt-0.5">
                             <Lightbulb size={16} />
                        </div>
                        <div className="text-sm text-yellow-900">
                            <span className="block font-bold mb-0.5">Check-out Reminder</span>
                            Complete check-out procedures at {data.hotel.name} by 11:00 AM.
                        </div>
                    </div>
                )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const ActivityCard: React.FC<{ activity: Activity }> = ({ activity }) => {
    return (
        <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg hover:border-blue-200 transition-all duration-300 relative overflow-hidden group">
            {/* Category Banner */}
            {activity.category && (
                <div className="absolute top-0 right-0 bg-booking-lightBlue text-booking-blue text-[10px] font-bold px-3 py-1.5 rounded-bl-xl uppercase tracking-wider">
                    {activity.category}
                </div>
            )}

            <div className="flex justify-between items-start mb-3">
                <h4 className="text-lg font-bold text-gray-900 pr-8 group-hover:text-booking-blue transition-colors">{activity.name}</h4>
            </div>
            
            <p className="text-gray-600 text-sm mb-5 leading-relaxed">{activity.description}</p>
            
            <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-gray-50">
                 <div className="flex items-center gap-1.5 text-xs text-gray-500 font-medium bg-gray-50 px-2.5 py-1.5 rounded-lg max-w-[70%]">
                    <MapPin size={14} className="text-gray-400 shrink-0" />
                    <span className="truncate">{activity.location}</span>
                 </div>
                 
                 <div className="flex items-center gap-3">
                     {activity.scheduled_time && (
                        <div className="flex items-center gap-1.5 text-xs text-gray-500 bg-gray-100 px-2.5 py-1.5 rounded-lg">
                            <Clock size={14} className="text-gray-500" />
                            <span>{activity.scheduled_time}</span>
                        </div>
                     )}
                     <div className="font-bold text-gray-900 text-lg">
                        ${activity.cost}
                     </div>
                 </div>
            </div>
        </div>
    )
}
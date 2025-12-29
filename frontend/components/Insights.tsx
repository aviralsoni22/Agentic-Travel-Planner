import React from 'react';
import { TripPlan } from '../types';
import { Lightbulb, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

interface InsightsProps {
  data: TripPlan;
}

export const Insights: React.FC<InsightsProps> = ({ data }) => {
  // SAFEGUARD: Default to empty array if failures is null
  const failures = data.failures || [];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-8 relative overflow-hidden">
      {/* Decorative background element */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-yellow-50 rounded-bl-full -mr-8 -mt-8 opacity-50 pointer-events-none"></div>

      <div className="flex items-center gap-3 mb-8 relative z-10">
        <div className="bg-booking-yellow/10 p-2.5 rounded-xl">
          <Lightbulb className="text-booking-yellow fill-booking-yellow" size={24} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Agent Strategy & Insights</h2>
          <p className="text-gray-500 text-sm">Reasoning traces for your itinerary</p>
        </div>
      </div>

      <div className="grid gap-4">
        <InsightItem
          title="Flight Selection"
          content={data.trace?.flight_component || "No insights available"}
          status={data.flights ? "success" : "error"}
          extra={failures.filter(f => f.component === 'flight').map((fail, i) => (
            <div key={i} className="mt-3 text-red-700 text-xs font-semibold bg-red-50 p-3 rounded-lg border border-red-100 inline-block">
              {fail.reason}
            </div>
          ))}
        />

        <InsightItem
          title="Hotel Selection"
          content={data.trace?.hotel_component || "No insights available"}
          status={data.hotel ? "success" : "error"}
          // FIX IS HERE: Used the safe 'failures' variable instead of data.failures
          extra={failures.filter(f => f.component === 'hotel').map((fail, i) => (
            <div key={i} className="mt-3 text-red-700 text-xs font-semibold bg-red-50 p-3 rounded-lg border border-red-100 inline-block">
              {fail.reason}
            </div>
          ))}
        />

        <InsightItem
          title="Activity Selection"
          content={data.trace?.activity_component || "No insights available"}
          status={data.itinerary_by_day && data.itinerary_by_day.length > 0 ? "success" : "error"}
          extra={failures.filter(f => f.component === 'activity').map((fail, i) => (
            <div key={i} className="mt-3 text-red-700 text-xs font-semibold bg-red-50 p-3 rounded-lg border border-red-100 inline-block">
              {fail.reason}
            </div>
          ))}
        />

        <InsightItem
          title="Budget Calculation"
          content={data.trace?.budgeting || "No insights available"}
          status={failures.some(f => f.component === 'budgeting') ? "error" : "success"}
          extra={failures.filter(f => f.component === 'budgeting').map((fail, i) => (
            <div key={i} className="mt-3 text-red-700 text-xs font-semibold bg-red-50 p-3 rounded-lg border border-red-100 inline-block">
              {fail.reason}
            </div>
          ))}
        />
      </div>
    </div>
  );
};

const InsightItem = ({ title, content, status, extra }: any) => {
  let icon;

  // Choose icon based on status
  switch (status) {
    case 'success':
      icon = <CheckCircle2 className="text-green-600" size={20} />;
      break;
    case 'error':
      icon = <XCircle className="text-red-600" size={20} />;
      break;
    case 'warning':
      icon = <AlertCircle className="text-orange-500" size={20} />;
      break;
    case 'neutral':
    default:
      icon = <CheckCircle2 className="text-gray-400" size={20} />;
      break;
  }

  return (
    <div className={`group flex gap-4 p-5 rounded-xl bg-gray-50 hover:bg-white hover:shadow-md border border-transparent hover:border-gray-100 transition-all duration-200`}>
      <div className={`mt-0.5 bg-white p-2 rounded-full shadow-sm border border-gray-100 shrink-0 h-fit`}>
        {icon}
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-bold text-gray-900 mb-1">
          {title}
        </h4>
        <p className="text-gray-600 text-sm leading-relaxed">{content}</p>
        {extra}
      </div>
    </div>
  )
}
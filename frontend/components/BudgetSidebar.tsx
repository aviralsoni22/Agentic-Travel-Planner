import React from 'react';
import { TripPlan } from '../types';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Wallet, Info, Sparkles } from 'lucide-react';
import { formatCurrency } from '../utils/format';

interface BudgetSidebarProps {
  data: TripPlan;
  onOpenChat: () => void;
}

export const BudgetSidebar: React.FC<BudgetSidebarProps> = ({ data, onOpenChat }) => {
  const flightsCost = data.flights?.total_price || 0;
  const hotelCost = data.hotel?.total_cost || 0;
  const activitiesCost = (data.itinerary_by_day || []).reduce((acc, day) => {
    return acc + day.activities.reduce((sum, act) => sum + act.cost, 0);
  }, 0);

  const chartData = [
    { name: 'Flights', value: flightsCost, color: '#003b95' },
    { name: 'Hotel', value: hotelCost, color: '#006ce4' },
    { name: 'Activities', value: activitiesCost, color: '#febb02' },
  ].filter(d => d.value > 0);

  const isOverBudget = data.remaining_budget < 0;

  return (
    <div className="space-y-6 sticky top-8">
      {/* Budget Summary Card */}
      <div className={`rounded-2xl p-6 text-white shadow-xl relative overflow-hidden transition-all duration-500 ${isOverBudget ? 'bg-gradient-to-br from-red-600 to-red-800' : 'bg-gradient-to-br from-booking-success to-green-800'}`}>
        <div className="absolute -top-4 -right-4 p-4 opacity-10 rotate-12">
          <Wallet size={100} />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <span className="bg-white/20 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm border border-white/10">
              {isOverBudget ? 'Budget Exceeded' : 'Under Budget'}
            </span>
          </div>
          <div className="text-5xl font-extrabold mb-1 tracking-tight">
            {data.remaining_budget < 0 ? '-' : '+'}{formatCurrency(Math.abs(data.remaining_budget)).replace('USD', '').trim()}
          </div>
          <div className="text-sm opacity-90 font-medium ml-1">Remaining funds available</div>
        </div>
      </div>

      {/* Breakdown Card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h3 className="font-bold text-gray-900 mb-6 flex items-center justify-between">
          <span>Trip Cost Breakdown</span>
          <span className="text-booking-blue bg-blue-50 px-2.5 py-1 rounded text-xs font-bold">USD</span>
        </h3>

        <div className="h-64 w-full relative mb-8">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                innerRadius={65}
                outerRadius={85}
                paddingAngle={4}
                dataKey="value"
                stroke="none"
                cornerRadius={4}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [formatCurrency(value), 'Cost']}
                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', padding: '12px' }}
                itemStyle={{ fontWeight: 'bold', color: '#1a1a1a' }}
              />
            </PieChart>
          </ResponsiveContainer>
          {/* Center Total */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-gray-400 text-[10px] uppercase font-bold tracking-widest mb-1">Total</span>
            <span className="text-gray-900 text-2xl font-extrabold tracking-tight">{formatCurrency(data.total_cost).replace('.00', '')}</span>
          </div>
        </div>

        <div className="space-y-3">
          {chartData.map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: item.color }}></div>
                <span className="text-sm font-semibold text-gray-700">{item.name}</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{formatCurrency(item.value)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* AI Assistant Promo */}
      <div onClick={onOpenChat} className="bg-gradient-to-r from-booking-blue to-blue-800 rounded-2xl shadow-lg p-1 overflow-hidden group cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
        <div className="bg-blue-900/40 backdrop-blur-xl rounded-xl p-5 relative overflow-hidden">
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-booking-yellow rounded-full opacity-20 blur-2xl group-hover:opacity-30 transition-opacity"></div>

          <div className="relative z-10 flex flex-col items-center text-center">
            <div className="bg-white/10 w-12 h-12 rounded-full flex items-center justify-center mb-3 backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-transform">
              <Sparkles className="text-booking-yellow" size={20} />
            </div>
            <h3 className="font-bold text-lg text-white mb-2">Need Local Tips?</h3>
            <p className="text-sm text-blue-100 mb-4 leading-relaxed">
              Chat with our Gemini Agent for real-time advice on {data.destination.split(',')[0]}.
            </p>
            <button className="bg-white text-booking-blue text-sm font-bold py-2.5 px-6 rounded-full hover:bg-blue-50 transition-colors w-full shadow-lg">
              Start Chat
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';

export const Navbar: React.FC = () => {
  return (
    <nav className="bg-booking-blue text-white px-4 md:px-8 h-20 flex items-center justify-between sticky top-0 z-50 shadow-md">
       <div className="font-bold text-2xl tracking-tighter flex items-center gap-2 cursor-pointer" onClick={() => window.location.reload()}>
          <span className="text-booking-yellow text-3xl">.</span>Booking.ai
       </div>
       <div className="hidden md:flex gap-4 text-sm font-bold">
          <button className="px-4 py-2 rounded-full hover:bg-white/10 transition-colors">USD</button>
          <button className="px-4 py-2 rounded-full hover:bg-white/10 flex items-center gap-2 transition-colors">
              <img src="https://flagcdn.com/w20/us.png" alt="US" className="w-5 h-3.5 rounded-sm object-cover" />
              <span>EN</span>
          </button>
          <button className="px-5 py-2 rounded-full border border-white/30 bg-transparent hover:bg-white/10 transition-colors">Register</button>
          <button className="px-5 py-2 rounded-full bg-white text-booking-blue hover:bg-gray-100 transition-colors shadow-sm">Sign in</button>
       </div>
    </nav>
  );
};

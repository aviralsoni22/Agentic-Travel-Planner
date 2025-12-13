import React from 'react';

export const Footer = () => {
  return (
    <footer className="bg-booking-blue text-white mt-12 py-10">
        <div className="max-w-7xl mx-auto px-4 md:px-8 grid grid-cols-2 md:grid-cols-4 gap-8 text-sm">
            <div>
                <h4 className="font-bold mb-4">Support</h4>
                <ul className="space-y-2 opacity-80">
                    <li>Manage your trips</li>
                    <li>Customer Service</li>
                    <li>Safety Resource Center</li>
                </ul>
            </div>
             <div>
                <h4 className="font-bold mb-4">Discover</h4>
                <ul className="space-y-2 opacity-80">
                    <li>Genius loyalty program</li>
                    <li>Seasonal and holiday deals</li>
                    <li>Travel articles</li>
                </ul>
            </div>
             <div>
                <h4 className="font-bold mb-4">Terms and settings</h4>
                <ul className="space-y-2 opacity-80">
                    <li>Privacy & cookies</li>
                    <li>Terms & conditions</li>
                    <li>Partner dispute</li>
                </ul>
            </div>
             <div>
                <h4 className="font-bold mb-4">Partners</h4>
                <ul className="space-y-2 opacity-80">
                    <li>Extranet login</li>
                    <li>Partner help</li>
                    <li>Become an affiliate</li>
                </ul>
            </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 md:px-8 mt-10 pt-8 border-t border-blue-800 text-center text-xs opacity-60">
            Copyright © 1996–2025 Booking.ai™. All rights reserved. <br/>
            This is a concept application demonstrating Agentic AI using CrewAI and Gemini.
        </div>
    </footer>
  )
}
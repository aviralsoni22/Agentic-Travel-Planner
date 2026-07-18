import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Sparkles, Bot, User, Loader2 } from 'lucide-react';
import { TripPlan } from '../types';
import { sendChatMessage } from '../services/gemini';

interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
  tripData: TripPlan;
}

interface Message {
  role: 'user' | 'model';
  text: string;
}

const FormattedText = ({ text }: { text: string }) => {
  const lines = text.split('\n');

  return (
    <>
      {lines.map((line, i) => (
        <div key={i} className={`${line.trim().startsWith('*') && !line.trim().startsWith('**') ? 'pl-4' : ''} min-h-[1.2em]`}>
          {parseLine(line)}
        </div>
      ))}
    </>
  );
};

const parseLine = (text: string) => {
  // Regex to capture **bold** text
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-bold">{part.slice(2, -2)}</strong>;
    }
    return <span key={index}>{part}</span>;
  });
};

export const ChatWidget: React.FC<ChatWidgetProps> = ({ isOpen, onClose, tripData }) => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'model', text: `Hi! I'm your Booking.ai travel assistant. I see you're planning a trip to ${tripData.destination}. How can I help you?` }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input;
    const history = messages;  // prior turns, before appending this one
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      // Chat is proxied through the backend (/api/chat); the Gemini key stays server-side.
      const reply = await sendChatMessage(userMessage, history, tripData);
      setMessages(prev => [...prev, { role: 'model', text: reply }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [
        ...prev,
        { role: 'model', text: "I'm sorry, I'm having trouble connecting right now. Please try again." }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-6 right-6 w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 flex flex-col overflow-hidden animate-in slide-in-from-bottom-10 fade-in duration-300 h-[500px]">
      {/* Header */}
      <div className="bg-booking-blue p-4 flex justify-between items-center text-white">
        <div className="flex items-center gap-2">
          <div className="bg-white/20 p-1.5 rounded-full">
            <Sparkles size={16} className="text-booking-yellow" />
          </div>
          <h3 className="font-bold">Booking.ai Assistant</h3>
        </div>
        <button onClick={onClose} className="hover:bg-white/20 p-1 rounded-full transition-colors">
          <X size={18} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-gray-200 text-gray-600' : 'bg-booking-blue text-white'}`}>
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                ? 'bg-white border border-gray-200 text-gray-800 rounded-tr-none shadow-sm'
                : 'bg-blue-50 text-blue-900 rounded-tl-none border border-blue-100'
              }`}>
              <FormattedText text={msg.text} />
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-booking-blue text-white flex items-center justify-center shrink-0">
              <Bot size={16} />
            </div>
            <div className="bg-blue-50 p-3 rounded-2xl rounded-tl-none border border-blue-100 flex items-center gap-2">
              <Loader2 size={16} className="animate-spin text-booking-blue" />
              <span className="text-xs text-blue-800 font-medium">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about your trip..."
            className="flex-1 bg-gray-100 text-gray-900 placeholder-gray-500 border-transparent focus:bg-white focus:border-booking-blue focus:ring-0 rounded-xl px-4 py-2.5 text-sm transition-all outline-none"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-booking-blue text-white p-2.5 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};
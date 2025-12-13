import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Sparkles, Bot, User, Loader2 } from 'lucide-react';
import { Chat } from "@google/genai";
import { TripPlan } from '../types';
import { initializeGeminiChat } from '../services/gemini';

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
  const [chatSession, setChatSession] = useState<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !chatSession) {
      // Initialize Gemini Client via Service
      const systemInstruction = `You are a helpful and enthusiastic travel assistant for Booking.ai.
          You are currently assisting a user with their trip to ${tripData.destination}.
          
          Here is the full trip context in JSON format:
          ${JSON.stringify(tripData)}

          Rules:
          1. Be concise and helpful.
          2. Use the provided JSON data to answer questions about budget, flights, hotels, and activities.
          3. If the user asks for recommendations not in the JSON, provide general suggestions for ${tripData.destination}.
          4. Keep the tone professional yet friendly, like a high-end travel concierge.
          5. Do not hallucinate data that isn't there, but you can infer from the destination.
          6. Format your response with simple line breaks or bullet points if needed.
          `;
          
      const chat = initializeGeminiChat(process.env.API_KEY || '', systemInstruction);
      setChatSession(chat);
    }
  }, [isOpen, tripData, chatSession]);

  const handleSend = async () => {
    if (!input.trim() || !chatSession) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const result = await chatSession.sendMessageStream({ message: userMessage });
      
      let fullResponse = "";
      let isFirstChunk = true;

      for await (const chunk of result) {
        const text = chunk.text;
        if (text) {
          fullResponse += text;
          
          if (isFirstChunk) {
            // First chunk received: stop "thinking" and add the message bubble
            setIsLoading(false);
            setMessages(prev => [...prev, { role: 'model', text: fullResponse }]);
            isFirstChunk = false;
          } else {
            // Subsequent chunks: update the existing bubble
            setMessages(prev => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1].text = fullResponse;
              return newMessages;
            });
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setIsLoading(false);
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
                <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed ${
                   msg.role === 'user' 
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
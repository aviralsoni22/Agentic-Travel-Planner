import { TripPlan } from '../types';

// Chat goes through the backend so the Gemini key stays server-side.
// Local dev uses the Vite proxy ('/api'); production builds set VITE_API_BASE to the backend URL.
const API_URL = import.meta.env.VITE_API_BASE || '/api';

export interface ChatTurn {
  role: 'user' | 'model';
  text: string;
}

export const sendChatMessage = async (
  message: string,
  history: ChatTurn[],
  trip: TripPlan,
): Promise<string> => {
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history, trip }),
  });
  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);
  const data = await res.json();
  return data.reply as string;
};

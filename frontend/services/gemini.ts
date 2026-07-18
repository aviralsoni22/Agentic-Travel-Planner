import { TripPlan } from '../types';

// Chat now goes through the backend (/api/chat) so the Gemini key stays server-side.
const API_URL = '/api';

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

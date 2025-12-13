import { GoogleGenAI, Chat } from "@google/genai";

export const initializeGeminiChat = (apiKey: string, systemInstruction: string): Chat => {
  const ai = new GoogleGenAI({ apiKey });
  
  return ai.chats.create({
    model: 'gemini-2.5-flash',
    config: {
      systemInstruction,
    },
  });
};
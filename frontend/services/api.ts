import { TripRequest, TripPlan } from '../types';

// Use the proxy path defined in vite.config.ts
const API_URL = '/api';

interface PollResponse {
  status: 'queued' | 'processing' | 'completed' | 'failed';
  task_id: string;
  plan?: TripPlan;
  error?: string;
}

export const generateItinerary = async (request: TripRequest): Promise<TripPlan> => {
  try {
    console.log("🚀 Sending request to backend...", request);

    // 1. Start the Task (Note: connecting to /api/plan)
    const startRes = await fetch(`${API_URL}/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source: request.origin, 
        destination: request.destination,
        start_date: request.startDate,
        end_date: request.endDate,
        num_travelers: request.travelers,
        budget: request.budget,
        interests: request.interests,
        group_category: request.groupType,
        currency: "USD"
      }),
    });

    if (!startRes.ok) {
      const err = await startRes.text();
      console.error("Backend Error:", err);
      throw new Error(`Failed to start planning: ${startRes.statusText}`);
    }

    const { task_id } = await startRes.json();
    console.log(`✅ Task Started: ${task_id}`);

    // 2. Poll for Results
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const statusRes = await fetch(`${API_URL}/plan/status/${task_id}`);
          if (!statusRes.ok) return;

          const data: PollResponse = await statusRes.json();
          console.log(`Polling status: ${data.status}`);

          if (data.status === 'completed' && data.plan) {
            clearInterval(interval);
            
            const finalPlan = data.plan;
            // Ensure trip_duration is set
            if (!finalPlan.trip_duration) {
               finalPlan.trip_duration = request.duration || 3;
            }
            
            resolve(finalPlan);
          } 
          else if (data.status === 'failed') {
            clearInterval(interval);
            reject(new Error(data.error || "Agents failed to generate plan"));
          }
        } catch (e) {
          console.warn("Polling error...", e);
        }
      }, 5000); 
    });

  } catch (error) {
    console.error("API Service Error:", error);
    throw error;
  }
};

// Alias for compatibility
export const fetchTripPlan = generateItinerary;
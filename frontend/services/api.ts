import { TripRequest, TripPlan } from '../types';

// Use the proxy path defined in vite.config.ts
const API_URL = '/api';

interface PollResponse {
  status: 'queued' | 'processing' | 'completed' | 'failed';
  task_id: string;
  plan?: TripPlan;
  error?: string;
}

// Set this to true to use fake data and avoid API calls
const USE_MOCK = false;

const MOCK_TRIP_PLAN: TripPlan = {
  destination: "Paris, France",
  start_date: "2025-06-15",
  end_date: "2025-06-20",
  num_travelers: 2,
  group_category: "Couple",
  interests: ["Art", "Food", "Romance"],
  failures: [],
  flights: {
    outbound_airline: "Air France",
    outbound_flight_number: "AF123",
    outbound_departure_time: "2025-06-15T10:00:00",
    outbound_arrival_time: "2025-06-15T18:30:00",
    outbound_price: 1200,
    outbound_booking_url: "#",
    outbound_discount_info: null,
    return_airline: "Air France",
    return_flight_number: "AF456",
    return_departure_time: "2025-06-20T14:00:00",
    return_arrival_time: "2025-06-20T22:30:00",
    return_price: 1100,
    return_booking_url: "#",
    return_discount_info: null,
    total_price: 2300
  },
  hotel: {
    name: "Hotel Regina Louvre",
    address: "2 Place des Pyramides, 75001 Paris, France",
    check_in: "2025-06-15",
    check_out: "2025-06-20",
    total_cost: 2500,
    rating: 9.2,
    image_url: "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=1000",
    booking_url: "#",
    discount_info: null
  },
  itinerary_by_day: [
    {
      day: "2025-06-15",
      notes: "Arrival and settling in.",
      activities: [
        {
          name: "Check-in & Relax",
          description: "Arrive at hotel and freshen up.",
          category: "Relaxation",
          cost: 0,
          location: "Hotel Regina Louvre",
          scheduled_time: "19:00",
          booking_url: null,
          discount_info: null
        }
      ]
    },
    {
      day: "2025-06-16",
      notes: "Exploring the classics.",
      activities: [
        {
          name: "Louvre Museum Tour",
          description: "Guided tour of the world's most famous museum.",
          category: "Culture",
          cost: 40,
          location: "Rue de Rivoli",
          scheduled_time: "10:00",
          booking_url: "#",
          discount_info: null
        },
        {
          name: "Seine River Cruise",
          description: "Romantic dinner cruise at sunset.",
          category: "Romance",
          cost: 150,
          location: "Port de la Bourdonnais",
          scheduled_time: "20:00",
          booking_url: "#",
          discount_info: null
        }
      ]
    }
  ],
  total_cost: 4990,
  remaining_budget: 10,
  trace: {
    flight_component: "Selected non-stop flights for convenience.",
    hotel_component: "Chose distinct luxury option near Louvre.",
    activity_component: "Balanced museum visits with romantic leisure.",
    budgeting: "Slightly optimized hotel cost to fit cruise."
  }
};

export const generateItinerary = async (request: TripRequest): Promise<TripPlan> => {
  if (USE_MOCK) {
    console.log("⚠️ USING MOCK DATA - NO API CALLS MADE ⚠️");
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    return MOCK_TRIP_PLAN;
  }

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
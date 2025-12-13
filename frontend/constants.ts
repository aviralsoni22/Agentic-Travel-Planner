import { TripPlan } from './types';

export const MOCK_TRIP_DATA: TripPlan = {
  destination: "Panaji, Goa, India",
  start_date: "2026-01-10",
  end_date: "2026-01-13",
  trip_duration: 3,
  num_travelers: 2,
  group_category: "Boys only",
  interests: ["Clubs", "Water Sports", "Food", "Forts", "Beaches"],
  failures: [
    {
      component: "hotel",
      reason: "No hotels found in Panaji, Goa, India under 18.74 USD remaining budget after flights.",
      tool_error: null
    }
  ],
  flights: {
    airline: "IndiGo",
    flight_number: "6E-123",
    departure_time: "10:00 AM",
    arrival_time: "12:30 PM",
    return_departure_time: "04:00 PM",
    return_arrival_time: "06:30 PM",
    total_price: 681.54,
    booking_url: null,
    discount_info: null
  },
  hotel: null, // As per JSON, hotel failed
  itinerary_by_day: [
    {
      day: "2026-01-10",
      activities: [
        {
          name: "Haryali Pure Veg Restaurant",
          description: "Authentic Goan vegetarian cuisine.",
          category: "catering",
          cost: 50.0,
          location: "Rua Cunha Rivara, Fontainhas, Panaji - 403001, Goa, India",
          scheduled_time: "19:00",
          booking_url: null,
          discount_info: null
        }
      ],
      notes: null
    },
    {
      day: "2026-01-11",
      activities: [],
      notes: null
    },
    {
      day: "2026-01-12",
      activities: [],
      notes: null
    },
    {
      day: "2026-01-13",
      activities: [],
      notes: null
    }
  ],
  total_cost: 731.54,
  remaining_budget: -31.54,
  trace: {
    flight_component: "Round trip flight found at minimum combined price 681.54 USD; within total budget if no other costs, but no margin for hotel or activities.",
    hotel_component: "No hotel available under remaining 18.74 USD—hard failure.",
    activity_component: "One affordable restaurant found and included at 50 USD.",
    budgeting: "Total cost: 681.54 (flights) + 0 (hotel) + 50 (activity) = 731.54. Remaining budget: -31.54 USD. Trip fails to meet minimum requirements due to lack of hotel."
  }
};
import { TripPlan } from './types';

export const MOCK_TRIP_DATA: TripPlan = {
  source: "New Delhi, India",
  destination: "Panaji, Goa, India",
  start_date: "2026-01-10",
  end_date: "2026-01-13",
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
    outbound_airline: "IndiGo",
    outbound_flight_number: "6E-123",
    outbound_departure_time: "2026-01-10T10:00:00",
    outbound_arrival_time: "2026-01-10T12:30:00",
    outbound_price: 340.77,
    outbound_booking_url: null,
    outbound_discount_info: null,
    return_airline: "IndiGo",
    return_flight_number: "6E-456",
    return_departure_time: "2026-01-13T16:00:00",
    return_arrival_time: "2026-01-13T18:30:00",
    return_price: 340.77,
    return_booking_url: null,
    return_discount_info: null,
    total_price: 681.54
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

export interface Failure {
  component: string;
  reason: string;
  tool_error: string | null;
}

export interface Flight {
  airline: string;
  flight_number: string;
  departure_time: string | null;
  arrival_time: string | null;
  return_departure_time: string | null;
  return_arrival_time: string | null;
  total_price: number;
  booking_url: string | null;
  discount_info: string | null;
}

export interface Hotel {
  name: string;
  address: string;
  rating: number;
  price_per_night: number;
  total_price: number;
  check_in: string;
  check_out: string;
  image_url: string;
}

export interface Activity {
  name: string;
  description: string;
  category: string;
  cost: number;
  location: string;
  scheduled_time: string | null;
  booking_url: string | null;
  discount_info: string | null;
}

export interface DailyItinerary {
  day: string;
  activities: Activity[];
  notes: string | null;
}

export interface Trace {
  flight_component: string;
  hotel_component: string;
  activity_component: string;
  budgeting: string;
}

export interface TripPlan {
  destination: string;
  start_date: string;
  end_date: string;
  trip_duration: number;
  num_travelers: number;
  group_category: string;
  interests: string[];
  failures: Failure[];
  flights: Flight | null;
  hotel: Hotel | null;
  itinerary_by_day: DailyItinerary[];
  total_cost: number;
  remaining_budget: number;
  trace: Trace;
}

export interface TripRequest {
  origin: string;
  destination: string;
  startDate: string;
  endDate: string;
  budget: number;
  duration: number;
  groupType: string;
  travelers: number;
  interests: string;
}

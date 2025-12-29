export interface Failure {
  component: string;
  reason: string;
  tool_error: string | null;
}

export interface FlightSummary {
  outbound_airline: string;
  outbound_flight_number: string;
  outbound_departure_time: string;
  outbound_arrival_time: string;
  outbound_price: number;
  outbound_booking_url: string | null;
  outbound_discount_info: string | null;
  outbound_departure_timezone?: string;
  outbound_arrival_timezone?: string;

  return_airline: string;
  return_flight_number: string;
  return_departure_time: string;
  return_arrival_time: string;
  return_price: number;
  return_booking_url: string | null;
  return_discount_info: string | null;
  return_departure_timezone?: string;
  return_arrival_timezone?: string;

  total_price: number;
}

export interface HotelSummary {
  name: string;
  address: string;
  check_in: string;
  check_out: string;
  total_cost: number;
  booking_url: string | null;
  discount_info: string | null;
  // Extras not in backend summary, but kept optional if we want to fallback/mock
  rating?: number;
  image_url?: string;
  nightly_rate?: number;
}

export interface Activity {
  name: string;
  description: string;
  category: string | null;
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
  flight_component?: string;
  hotel_component?: string;
  activity_component?: string;
  budgeting?: string;
  [key: string]: string | undefined;
}

export interface TripPlan {
  destination: string;
  start_date: string;
  end_date: string;
  // trip_duration removed from backend
  num_travelers: number;
  group_category: string;
  interests: string[];
  failures: Failure[] | null;
  flights: FlightSummary | null;
  hotel: HotelSummary | null;
  itinerary_by_day: DailyItinerary[] | null;
  total_cost: number | null;
  remaining_budget: number | null;
  trace: Trace | null;
}

export interface TripRequest {
  origin: string;
  destination: string;
  startDate: string;
  endDate: string;
  budget: number;
  groupType: string;
  travelers: number;
  interests: string;
}

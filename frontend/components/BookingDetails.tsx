import React, { useMemo } from 'react';
import { TripPlan, FlightSummary } from '../types';
import { Plane, MapPin, Calendar, ExternalLink, AlertTriangle, ArrowRight, Clock } from 'lucide-react';
import { formatCurrency, formatTime, formatDate, formatTimezone } from '../utils/format';

interface BookingDetailsProps {
    data: TripPlan;
}

export const BookingDetails: React.FC<BookingDetailsProps> = ({ data }) => {
    // Calculate duration on frontend since backend removed it
    const tripDuration = useMemo(() => {
        if (!data.start_date || !data.end_date) return 0;
        const start = new Date(data.start_date);
        const end = new Date(data.end_date);
        const diffTime = Math.abs(end.getTime() - start.getTime());
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    }, [data.start_date, data.end_date]);

    return (
        <div className="space-y-8 mb-10">
            <div className="flex items-center gap-3 pb-2">
                <div className="bg-booking-blue/10 p-2 rounded-lg">
                    <Plane className="text-booking-blue" size={24} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Flight Itinerary</h2>
            </div>

            {data.flights && (
                <div className="grid grid-cols-1 gap-6">
                    {/* Outbound Flight Card */}
                    <FlightCard
                        type="Outbound"
                        flight={data.flights}
                        numTravelers={data.num_travelers}
                        from={data.source ? data.source.split(',')[0] : 'Origin'}
                        to={data.destination ? data.destination.split(',')[0] : 'Destination'}

                        // Pass specific outbound fields
                        airline={data.flights.outbound_airline}
                        flightNumber={data.flights.outbound_flight_number}
                        departTime={data.flights.outbound_departure_time}
                        arriveTime={data.flights.outbound_arrival_time}
                        departTimezone={data.flights.outbound_departure_timezone}
                        arriveTimezone={data.flights.outbound_arrival_timezone}
                        price={data.flights.outbound_price}
                    />

                    {/* Return Flight Card */}
                    <FlightCard
                        type="Return"
                        flight={data.flights}
                        numTravelers={data.num_travelers}
                        from={data.destination ? data.destination.split(',')[0] : 'Destination'}
                        to={data.source ? data.source.split(',')[0] : 'Origin'}

                        // Pass specific return fields
                        airline={data.flights.return_airline}
                        flightNumber={data.flights.return_flight_number}
                        departTime={data.flights.return_departure_time}
                        arriveTime={data.flights.return_arrival_time}
                        departTimezone={data.flights.return_departure_timezone}
                        arriveTimezone={data.flights.return_arrival_timezone}
                        price={data.flights.return_price}
                    />
                </div>
            )}

            {/* Hotel Section */}
            <div className="flex items-center gap-3 pt-6 pb-2 border-t border-gray-200 mt-8">
                <div className="bg-booking-blue/10 p-2 rounded-lg">
                    <MapPin className="text-booking-blue" size={24} />
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Accommodation</h2>
            </div>

            {data.hotel ? (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden flex flex-col md:flex-row group hover:shadow-md transition-all duration-300">
                    <div className="md:w-2/5 relative min-h-[260px] overflow-hidden">
                        <img
                            src={data.hotel.image_url || "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=1000"}
                            alt={data.hotel.name}
                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                        />
                        <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm text-booking-blue text-xs font-bold px-3 py-1.5 rounded-full shadow-sm flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-booking-blue rounded-full animate-pulse"></span>
                            Agent's Top Pick
                        </div>
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-6 pt-12">
                            <div className="flex items-center gap-2 text-white/90">
                                <MapPin size={16} />
                                <span className="text-sm font-medium truncate">{data.hotel.address}</span>
                            </div>
                        </div>
                    </div>

                    <div className="p-6 md:w-3/5 flex flex-col justify-between">
                        <div>
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-2xl font-bold text-gray-900 leading-tight mb-2">{data.hotel.name}</h3>
                                    <div className="flex items-center gap-2">
                                        {/* Use optional rating if available, else default */}
                                        <div className="bg-booking-blue text-white px-2.5 py-1 rounded text-sm font-bold">
                                            {data.hotel.rating ?? 9.0}
                                        </div>
                                        <span className="text-sm font-medium text-gray-700">Excellent</span>
                                        <span className="text-sm text-gray-400">• {data.hotel.total_cost > 200 ? 'Mid-range' : 'Budget'}</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-3xl font-bold text-booking-blue">{formatCurrency(data.hotel.total_cost)}</div>
                                    <div className="text-xs text-gray-500 font-medium">{tripDuration} nights total</div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                                    <div className="text-xs text-gray-400 uppercase tracking-wider mb-1 font-bold">Check-in</div>
                                    <div className="font-semibold text-gray-800 flex items-center gap-2">
                                        <Calendar size={16} className="text-booking-blue" />
                                        {/* Format as DD-MM-YYYY */}
                                        {data.hotel.check_in ? (() => {
                                            const d = new Date(data.hotel.check_in);
                                            return `${String(d.getDate()).padStart(2, '0')}-${String(d.getMonth() + 1).padStart(2, '0')}-${d.getFullYear()}`;
                                        })() : 'TBD'}
                                    </div>
                                </div>
                                <div className="bg-gray-50 p-3 rounded-xl border border-gray-100">
                                    <div className="text-xs text-gray-400 uppercase tracking-wider mb-1 font-bold">Check-out</div>
                                    <div className="font-semibold text-gray-800 flex items-center gap-2">
                                        <Calendar size={16} className="text-booking-blue" />
                                        {data.hotel.check_out ? (() => {
                                            const d = new Date(data.hotel.check_out);
                                            return `${String(d.getDate()).padStart(2, '0')}-${String(d.getMonth() + 1).padStart(2, '0')}-${d.getFullYear()}`;
                                        })() : 'TBD'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <button className="w-full bg-booking-blue text-white font-bold py-3.5 px-6 rounded-xl hover:bg-blue-800 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-blue-900/10">
                            View Reservation Details <ArrowRight size={18} />
                        </button>
                    </div>
                </div>
            ) : (
                <div className="bg-red-50 border border-red-100 rounded-2xl p-8 flex items-start gap-5">
                    <div className="bg-white p-3 rounded-full shrink-0 shadow-sm text-red-600">
                        <AlertTriangle size={24} />
                    </div>
                    <div>
                        <h3 className="text-red-900 font-bold text-xl mb-2">Accommodation Unavailable</h3>
                        <p className="text-red-700 leading-relaxed mb-4">
                            Based on your budget constraints after flight selection, we couldn't secure a hotel reservation.
                            {data.remaining_budget !== null && (
                                <span className="block mt-1">Remaining budget: <span className="font-bold font-mono bg-red-100 px-1 rounded">{formatCurrency(data.remaining_budget)}</span></span>
                            )}
                        </p>
                        <button className="text-red-800 text-sm font-bold underline hover:text-red-900">
                            Adjust Budget Parameters
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

interface FlightCardProps {
    type: string;
    // Don't pass full Flight object, pass values
    flight: FlightSummary;
    numTravelers: number;
    from: string;
    to: string;

    // Explicit overrides
    airline: string;
    flightNumber: string;
    departTime: string | null;
    arriveTime: string | null;
    departTimezone?: string;
    arriveTimezone?: string;
    price: number;
}

const FlightCard: React.FC<FlightCardProps> = ({ type, flight, numTravelers, from, to, airline, flightNumber, departTime, arriveTime, departTimezone, arriveTimezone, price }) => {
    // Parse times
    const dTime = formatTime(departTime);
    const aTime = formatTime(arriveTime);

    // Parse dates
    const dDate = formatDate(departTime || '');
    const aDate = formatDate(arriveTime || '');

    // Resolve timezones: Use explicit prop, otherwise search string, otherwise default to 'Local'
    const dTz = departTimezone ?? formatTimezone(departTime || '') ?? 'Local';
    const aTz = arriveTimezone ?? formatTimezone(arriveTime || '') ?? 'Local';

    // Split for styling (HH:MM and AM/PM)
    const [dClock, dAmpm] = dTime.split(' ');
    const [aClock, aAmpm] = aTime.split(' ');

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden relative group">
            {/* Left Color Bar */}
            <div className="absolute left-0 top-0 bottom-0 w-2 bg-booking-blue"></div>

            <div className="flex flex-col md:flex-row">
                {/* Main Ticket Info */}
                <div className="flex-1 p-6 pl-8">
                    <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-3">
                            <span className="bg-blue-50 text-booking-blue px-3 py-1 rounded-md text-xs font-bold uppercase tracking-wider border border-blue-100">
                                {type} Flight
                            </span>
                            <span className="text-gray-400 text-xs font-semibold">{flightNumber}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-500 text-xs font-bold">
                            <span className="w-2 h-2 rounded-full bg-green-500"></span>
                            Confirmed
                        </div>
                    </div>

                    <div className="flex items-center justify-between gap-6">
                        <div className="text-center min-w-[80px]">
                            <div className="text-2xl font-bold text-gray-900">{dClock}</div>
                            <div className="text-xs text-gray-400 font-bold uppercase mt-1 bg-gray-50 rounded px-1">{dAmpm}</div>
                            <div className="text-xs text-gray-500 font-medium mt-1">{dDate}</div>
                            <div className="text-[10px] text-gray-400 uppercase tracking-wider mt-0.5">{dTz || 'Local'}</div>
                            <div className="text-sm font-bold text-gray-600 mt-2">{from}</div>
                        </div>

                        <div className="flex-1 flex flex-col items-center relative px-4">
                            <div className="text-xs text-gray-400 mb-2 font-medium">Non-stop</div>
                            <div className="w-full h-[2px] bg-gray-200 relative flex items-center justify-between">
                                <div className="w-1.5 h-1.5 rounded-full bg-gray-300"></div>
                                <div className="absolute left-1/2 -translate-x-1/2 bg-white px-2">
                                    <Plane className="text-booking-blue rotate-90" size={16} />
                                </div>
                                <div className="w-1.5 h-1.5 rounded-full bg-gray-300"></div>
                            </div>
                            <div className="text-xs text-gray-400 mt-2 font-medium">{airline}</div>
                        </div>

                        <div className="text-center min-w-[80px]">
                            <div className="text-2xl font-bold text-gray-900">{aClock}</div>
                            <div className="text-xs text-gray-400 font-bold uppercase mt-1 bg-gray-50 rounded px-1">{aAmpm}</div>
                            <div className="text-xs text-gray-500 font-medium mt-1">{aDate}</div>
                            <div className="text-[10px] text-gray-400 uppercase tracking-wider mt-0.5">{aTz || 'Local'}</div>
                            <div className="text-sm font-bold text-gray-600 mt-2">{to}</div>
                        </div>
                    </div>
                </div>

                {/* Right Tear-off Stub */}
                <div className="relative md:w-48 bg-gray-50 p-6 flex flex-col justify-center border-t md:border-t-0 md:border-l border-dashed border-gray-300">
                    {/* Cutout circles for aesthetic */}
                    <div className="absolute -left-3 top-0 w-6 h-6 bg-[#f5f7fa] rounded-full hidden md:block"></div>
                    <div className="absolute -left-3 bottom-0 w-6 h-6 bg-[#f5f7fa] rounded-full hidden md:block"></div>

                    <div className="text-center">
                        <div className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-2">Class</div>
                        <div className="text-lg font-bold text-gray-900 mb-4">Economy</div>

                        <div className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-2">Per Person</div>
                        <div className="text-xl font-bold text-booking-blue mb-4">
                            {formatCurrency(price / Math.max(1, numTravelers))}
                        </div>

                        <button className="w-full bg-white border border-gray-300 text-gray-700 text-xs font-bold py-2 rounded hover:bg-gray-50 transition-colors">
                            Change
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
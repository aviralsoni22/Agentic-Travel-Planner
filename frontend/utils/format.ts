export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatDate = (dateStr: string): string => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  // Ensure we don't have timezone offset issues by treating the string as local if needed, 
  // but standard date parsing usually suffices for display if the input is YYYY-MM-DD
  return date.toLocaleDateString('en-US', { weekday: 'short', month: 'long', day: 'numeric' });
};

export const formatTime = (timeStr: string | null): string => {
  if (!timeStr) return '--:--';

  // If it's a full ISO string (YYYY-MM-DDTHH:MM...), extract the time part
  // We split by 'T' to get the time component, avoiding timezone shifts from Date parsing
  let timePart = timeStr;
  if (timeStr.includes('T')) {
    timePart = timeStr.split('T')[1];
  } else if (timeStr.includes(' ')) {
    // Handle "YYYY-MM-DD HH:MM" format just in case
    timePart = timeStr.split(' ')[1];
  }

  // Check if it's already in 12h format
  if (timePart.includes('M')) return timePart;

  // Parse HH:MM
  const parts = timePart.split(':');
  if (parts.length < 2) return timeStr; // Fallback

  const [hours, minutes] = parts;
  const h = parseInt(hours, 10);

  if (isNaN(h)) return timeStr; // Fallback if parsing fails

  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 || 12;

  // Return formatted time
  return `${h12}:${minutes} ${ampm}`;
};

// Extract a clean "GMT+5:30" / "GMT+1" / "GMT-4" / "GMT" from an ISO time's own offset.
export const formatTimezone = (timeStr: string): string => {
  if (!timeStr) return '';
  const match = timeStr.match(/([+-])(\d{2}):?(\d{2})(?!.*\d)|Z/);
  if (!match) return '';
  if (match[0] === 'Z') return 'GMT';
  const [, sign, hh, mm] = match;
  const hours = parseInt(hh, 10);
  const mins = parseInt(mm, 10);
  return `GMT${sign}${hours}${mins ? ':' + String(mins).padStart(2, '0') : ''}`;
};

// Timezone label as a GMT offset. Prefer the offset in the ISO string; otherwise compute it
// from an IANA name (e.g. "Asia/Kolkata") via Intl so it's correct regardless of viewer tz.
export const formatGmt = (tzName: string | undefined, isoTime: string): string => {
  const fromOffset = formatTimezone(isoTime);
  if (fromOffset) return fromOffset;

  if (tzName && isoTime) {
    try {
      const parts = new Intl.DateTimeFormat('en-US', {
        timeZone: tzName,
        timeZoneName: 'shortOffset',
      }).formatToParts(new Date(isoTime));
      const gmt = parts.find(p => p.type === 'timeZoneName')?.value;
      if (gmt) return gmt.replace('UTC', 'GMT'); // some engines emit "UTC+5:30"
    } catch {
      /* tzName isn't a valid IANA zone (e.g. "IST") — fall through */
    }
  }
  return tzName || 'Local';
};
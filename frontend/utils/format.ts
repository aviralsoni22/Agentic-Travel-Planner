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

export const formatTimezone = (timeStr: string): string => {
  if (!timeStr) return '';

  // Regex to look for +HH:MM or -HH:MM or Z at the end or late part of string
  // Matches: +05:30, -04:00, +0530, Z
  const match = timeStr.match(/([+-]\d{2}:?\d{2}|Z)/);

  if (match) {
    const tz = match[1];
    if (tz === 'Z') return 'GMT';
    return `GMT${tz}`;
  }

  return '';
};
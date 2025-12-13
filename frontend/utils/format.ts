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
  // Check if it's already in HH:MM format (24h) or has AM/PM
  if (timeStr.includes('M')) return timeStr; // e.g. 10:00 AM
  
  // Simple parser for HH:MM
  const [hours, minutes] = timeStr.split(':');
  const h = parseInt(hours, 10);
  const ampm = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 || 12;
  return `${h12}:${minutes} ${ampm}`;
};
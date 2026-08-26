/**
 * Formats ISO date strings, timestamps, or Date objects into a user-friendly date and time string.
 * Example output: "Aug 27, 2026, 12:17 AM"
 */
export function formatDateTime(dateInput) {
  if (!dateInput) return 'N/A';
  try {
    const d = new Date(dateInput);
    if (isNaN(d.getTime())) return String(dateInput);
    return d.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return String(dateInput);
  }
}

/**
 * Formats ISO date strings, timestamps, or Date objects into a user-friendly date-only string.
 * Example output: "Aug 27, 2026"
 */
export function formatDateOnly(dateInput) {
  if (!dateInput) return 'N/A';
  try {
    const d = new Date(dateInput);
    if (isNaN(d.getTime())) return String(dateInput);
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return String(dateInput);
  }
}

// The API sends timestamps as ISO-8601 strings in UTC,
// e.g. "2026-11-23T18:04:05+00:00". Show them as a short local date,
// e.g. "Nov 23, 2026". Returns "" for a missing or unparseable value.
export default function formatDate(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

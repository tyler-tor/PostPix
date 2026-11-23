// One place for every API call from the frontend.
//
// CSRF protection ("double submit"): the Flask backend sets a `csrf_token`
// cookie on every response. For any request that changes data
// (POST/PUT/PATCH/DELETE) we copy that cookie value into the `X-CSRFToken`
// header. Another website can make your browser *send* the cookie, but it
// cannot *read* it, so it cannot set the header, and Flask-WTF rejects the
// request with a 400.

export function getCookie(name) {
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.split("=").slice(1).join("=")) : null;
}

const SAFE_METHODS = ["GET", "HEAD", "OPTIONS"];

export default function apiFetch(url, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = new Headers(options.headers || {});
  if (!SAFE_METHODS.includes(method)) {
    const token = getCookie("csrf_token");
    if (token) headers.set("X-CSRFToken", token);
  }
  return fetch(url, { credentials: "same-origin", ...options, headers });
}

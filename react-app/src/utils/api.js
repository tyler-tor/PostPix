import apiFetch from "./apiFetch";

// JSON helper on top of apiFetch (which adds the CSRF header).
//
//   const { ok, data, errors } = await api("/api/posts/", { method: "POST", json: { caption } });
//
// It never throws: a network failure comes back as ok = false with a message in
// `errors`, so callers only need one code path for "it did not work".
export async function api(url, { method = "GET", json, form } = {}) {
  const options = { method };
  if (json !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(json);
  } else if (form) {
    options.body = form; // multipart; the browser sets the Content-Type
  }
  try {
    const response = await apiFetch(url, options);
    let data = {};
    try {
      data = await response.json();
    } catch {
      /* empty or non-JSON body */
    }
    return {
      ok: response.ok,
      status: response.status,
      data,
      errors: response.ok ? [] : data.errors || ["Something went wrong. Please try again."],
    };
  } catch {
    return {
      ok: false,
      status: 0,
      data: {},
      errors: ["Could not reach the server. Check your connection and try again."],
    };
  }
}

// Tiny notification store, outside Redux on purpose: toasts are short-lived UI
// feedback, not app data. Anything can call toast("Saved") or toast("Failed", "error");
// <Toaster /> shows them. Used with useSyncExternalStore.
let items = [];
let nextId = 1;
const listeners = new Set();
const emit = () => listeners.forEach((fn) => fn());

export const subscribe = (fn) => {
  listeners.add(fn);
  return () => listeners.delete(fn);
};
export const getToasts = () => items;

export const dismissToast = (id) => {
  items = items.filter((item) => item.id !== id);
  emit();
};

// kind: "info" | "error". Errors stay a little longer.
export const toast = (message, kind = "info") => {
  const id = nextId++;
  items = [...items.slice(-2), { id, message, kind }]; // at most 3 at once
  emit();
  setTimeout(() => dismissToast(id), kind === "error" ? 7000 : 4000);
  return id;
};

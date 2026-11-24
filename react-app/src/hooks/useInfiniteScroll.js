import { useEffect, useRef } from "react";

// Calls onMore() when the returned ref's element scrolls near the viewport
// (400px before it). Pass enabled = false when there is nothing more to load.
// `busy` is in the dependency list on purpose: after a page loads, a new
// observer is created, and it reports "already visible" right away, so a short
// page that does not fill the screen keeps loading until it does.
export default function useInfiniteScroll(onMore, enabled, busy) {
  const ref = useRef(null);
  useEffect(() => {
    const node = ref.current;
    if (!enabled || busy || !node || typeof IntersectionObserver === "undefined") return undefined;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) onMore();
      },
      { rootMargin: "400px" }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [onMore, enabled, busy]);
  return ref;
}

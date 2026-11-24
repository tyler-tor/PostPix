import React from "react";
import useInfiniteScroll from "../../hooks/useInfiniteScroll";
import "./LoadMore.css";

// Infinite scroll with a keyboard-friendly fallback: the next page loads by
// itself when this element scrolls near the viewport, and the button does the
// same on click or Enter. Renders nothing when there is nothing more to load.
const LoadMore = ({ hasMore, loading, onLoadMore, label = "Load more" }) => {
  const ref = useInfiniteScroll(onLoadMore, hasMore, loading);
  if (!hasMore) return null;
  return (
    <div ref={ref} className="load-more">
      <button type="button" className="load-more-button" onClick={onLoadMore} disabled={loading}>
        {loading ? "Loading..." : label}
      </button>
    </div>
  );
};

export default LoadMore;

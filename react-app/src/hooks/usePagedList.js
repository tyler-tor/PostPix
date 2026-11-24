import { useCallback, useEffect, useState } from "react";
import { api } from "../utils/api";

// A list that one screen owns and loads page by page (followers, following,
// people who liked a post). `dataKey` is the array's key in the JSON.
//   const { items, status, errors, hasMore, loadingMore, loadMore } = usePagedList(url, "followers");
// The server sends "nextCursor"; it is passed back as ?after=<cursor>.
export default function usePagedList(url, dataKey) {
  const [state, setState] = useState({ items: [], status: "loading", errors: [], nextCursor: null, loadingMore: false });

  useEffect(() => {
    let current = true;
    setState({ items: [], status: "loading", errors: [], nextCursor: null, loadingMore: false });
    api(url).then((res) => {
      if (!current) return;
      setState(
        res.ok
          ? { items: res.data[dataKey], status: "ready", errors: [], nextCursor: res.data.nextCursor, loadingMore: false }
          : { items: [], status: "error", errors: res.errors, nextCursor: null, loadingMore: false }
      );
    });
    return () => {
      current = false;
    };
  }, [url, dataKey]);

  const loadMore = useCallback(async () => {
    if (!state.nextCursor || state.loadingMore) return;
    setState((prev) => ({ ...prev, loadingMore: true }));
    const sep = url.includes("?") ? "&" : "?";
    const res = await api(`${url}${sep}after=${encodeURIComponent(state.nextCursor)}`);
    setState((prev) =>
      res.ok
        ? { ...prev, items: [...prev.items, ...res.data[dataKey]], nextCursor: res.data.nextCursor, loadingMore: false }
        : { ...prev, loadingMore: false, errors: res.errors }
    );
  }, [url, dataKey, state.nextCursor, state.loadingMore]);

  return { ...state, hasMore: !!state.nextCursor, loadMore };
}

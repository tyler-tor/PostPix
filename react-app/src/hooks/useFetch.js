import { useCallback, useEffect, useState } from "react";
import { api } from "../utils/api";

// Load a URL for a screen that keeps its own result (a modal list, search
// results). Not for data other screens share; that belongs in the store.
//   const { status, data, errors, reload } = useFetch("/api/users/3/followers");
// status: "loading" | "ready" | "error". Pass url = null to skip loading.
export default function useFetch(url) {
  const [state, setState] = useState({ status: "loading", data: null, errors: [] });

  const load = useCallback(() => {
    if (!url) return () => {};
    let current = true;
    setState((prev) => ({ ...prev, status: "loading" }));
    api(url).then((res) => {
      if (!current) return;
      setState(
        res.ok
          ? { status: "ready", data: res.data, errors: [] }
          : { status: "error", data: null, errors: res.errors }
      );
    });
    return () => {
      current = false;
    };
  }, [url]);

  useEffect(() => load(), [load]);
  return { ...state, reload: load };
}

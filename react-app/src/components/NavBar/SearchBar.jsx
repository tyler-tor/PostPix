import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { FiSearch } from "react-icons/fi";
import { api } from "../../utils/api";
import Avatar from "../ui/Avatar";

const DEBOUNCE_MS = 250;

// Type a username, get a list of matching people. The server does the
// matching (GET /api/users/search?q=), 250 ms after you stop typing, so
// nothing is downloaded until you search and only 10 people are ever returned.
// Results are plain links (Tab moves through them); Escape clears the box.
const SearchBar = () => {
  const [searchInput, setSearchInput] = useState("");
  const [results, setResults] = useState({ term: "", users: [], status: "idle" });
  const root = useRef(null);
  const term = searchInput.trim();

  useEffect(() => {
    if (!term) return undefined;
    let current = true; // ignore the answer if the user has typed more since
    const timer = setTimeout(async () => {
      setResults((prev) => ({ ...prev, status: "loading" }));
      const res = await api(`/api/users/search?q=${encodeURIComponent(term)}&limit=10`);
      if (!current) return;
      setResults(res.ok ? { term, users: res.data.users, status: "ready" } : { term, users: [], status: "error" });
    }, DEBOUNCE_MS);
    return () => {
      current = false;
      clearTimeout(timer);
    };
  }, [term]);

  // Click or focus leaving the search closes the list.
  useEffect(() => {
    if (!term) return undefined;
    const outside = (e) => {
      if (root.current && !root.current.contains(e.target)) setSearchInput("");
    };
    document.addEventListener("click", outside);
    return () => document.removeEventListener("click", outside);
  }, [term]);

  const showing = term && results.term === term;
  let status = "";
  if (showing && results.status === "ready") {
    status = results.users.length ? `${results.users.length} ${results.users.length === 1 ? "person" : "people"} found` : "No users with that username found!";
  }
  if (showing && results.status === "error") status = "Search failed. Try again.";

  return (
    <div className="search" role="search" ref={root}>
      <div className="search-inner">
        <FiSearch aria-hidden="true" />
        <label htmlFor="people-search" className="visually-hidden">
          Search people by username
        </label>
        <input
          id="people-search"
          type="search"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          onKeyDown={(e) => e.key === "Escape" && setSearchInput("")}
          placeholder="Search people"
          autoComplete="off"
          spellCheck="false"
        />
      </div>
      <div className="visually-hidden" role="status" aria-live="polite">
        {status}
      </div>
      {showing && (
        <div className="dropdown">
          {results.users.map((item) => (
            <Link key={item.id} to={`/${item.id}`} onClick={() => setSearchInput("")} className="dropdown-row">
              <Avatar src={item.profilePicture} size={2.25} />
              <span>
                <strong>{item.username}</strong>
                {(item.firstName || item.lastName) && (
                  <span className="dropdown-name">
                    {item.firstName} {item.lastName}
                  </span>
                )}
              </span>
            </Link>
          ))}
          {status && !results.users.length && <p className="dropdown-note">{status}</p>}
        </div>
      )}
    </div>
  );
};

export default SearchBar;

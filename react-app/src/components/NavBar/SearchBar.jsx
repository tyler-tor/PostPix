import React, { useEffect, useState } from "react";
import { NavLink } from "react-router";
import { api } from "../../utils/api";
import "./SearchBar.css";

const DEBOUNCE_MS = 250;

// Type a username, get a dropdown of matching people. The server does the
// matching (GET /api/users/search?q=), 250 ms after you stop typing, so
// nothing is downloaded until you search and only 10 people are ever returned.
const SearchBar = () => {
  const [searchInput, setSearchInput] = useState("");
  const [results, setResults] = useState({ term: "", users: [], status: "idle" });
  const term = searchInput.trim();

  useEffect(() => {
    if (!term) return undefined;
    let current = true; // ignore the answer if the user has typed more since
    const timer = setTimeout(async () => {
      setResults((prev) => ({ ...prev, status: "loading" }));
      const res = await api(`/api/users/search?q=${encodeURIComponent(term)}&limit=10`);
      if (!current) return;
      setResults(
        res.ok
          ? { term, users: res.data.users, status: "ready" }
          : { term, users: [], status: "error" }
      );
    }, DEBOUNCE_MS);
    return () => {
      current = false;
      clearTimeout(timer);
    };
  }, [term]);

  // Only show results for what is in the box right now.
  const showing = term && results.term === term;

  return (
    <div className="search-container">
      <div className="search-inner">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Search for a user"
        />
      </div>

      <div className="dropdown">
        {showing &&
          results.users.map((item) => (
            <NavLink
              key={item.id}
              to={`/${item.id}`}
              onClick={() => setSearchInput("")}
              className="dropdown-row"
            >
              <img src={item.profilePicture} className="search-pic" alt="" />
              <div className="search-dropdown-name">{item.username}</div>
            </NavLink>
          ))}
        {showing && results.status === "ready" && results.users.length === 0 && (
          <div>No users with that username found!</div>
        )}
        {showing && results.status === "error" && <div>Search failed. Try again.</div>}
      </div>
    </div>
  );
};

export default SearchBar;

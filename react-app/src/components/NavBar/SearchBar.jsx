import React, { useState } from "react";
import { NavLink } from "react-router";
import useFetch from "../../hooks/useFetch";
import "./SearchBar.css";

// Type a username, get a dropdown of matching people.
// (P23 moves the matching to the server; for now the list is fetched once.)
const SearchBar = () => {
  const [searchInput, setSearchInput] = useState("");
  const { data } = useFetch("/api/users/?limit=100");
  const users = data?.users ?? [];

  const term = searchInput.trim().toLowerCase();
  const matches = term
    ? users.filter((user) => user.username.toLowerCase().startsWith(term)).slice(0, 10)
    : [];

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
        {matches.map((item) => (
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
        {term && matches.length === 0 && <div>No users with that username found!</div>}
      </div>
    </div>
  );
};

export default SearchBar;

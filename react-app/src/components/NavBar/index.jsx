import React from "react";
import { NavLink, Link } from "react-router";
import { FiHome, FiGrid } from "react-icons/fi";
import Wordmark from "../Brand/Wordmark";
import SearchBar from "./SearchBar";
import AccountMenu from "./AccountMenu";
import NewPost from "../Post/NewPost";
import { FiPlusSquare } from "react-icons/fi";
import "./NavBar.css";

// Top bar on every screen: logo, search. The main links are the same <nav> in
// both layouts: on a computer they sit at the right of the top bar, on a phone
// the nav becomes a tab bar fixed to the bottom of the screen.
const NavBar = () => (
  <header className="topbar">
    <div className="topbar-inner">
      <Link to="/" className="topbar-logo" aria-label="Postpix home">
        <Wordmark size="sm" />
      </Link>
      <SearchBar />
      <nav className="mainnav" aria-label="Main">
        <NavLink to="/" end className="nav-link">
          <FiHome aria-hidden="true" />
          <span className="nav-label">Home</span>
        </NavLink>
        <NavLink to="/explore" className="nav-link">
          <FiGrid aria-hidden="true" />
          <span className="nav-label">Explore</span>
        </NavLink>
        <NewPost className="nav-link">
          <FiPlusSquare aria-hidden="true" />
          <span className="nav-label">New post</span>
        </NewPost>
        <AccountMenu />
      </nav>
    </div>
  </header>
);

export default NavBar;

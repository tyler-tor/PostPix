import React, { useState } from "react";
import { NavLink } from "react-router";
import ProfileDropDownMenu from "./ProfileDropDownMenu";
import Wordmark from "../Brand/Wordmark";
import SearchBar from "./SearchBar";
import NewPost from "../Post/NewPost";
import { AiOutlineCompass, AiFillHome } from "react-icons/ai";
import "./NavBar.css";

const NavBar = () => {

  return (
    <div className="navbar-container">
      <div className="navbar-child logo-portion">
        <NavLink to={`/`}>
          <div className="navbar-logo-container">
            <Wordmark size="sm" />
          </div>
        </NavLink>
      </div>
      <div className="navbar-child search-portion">
        <SearchBar />
      </div>
      <div className="navbar-child right-part-portion">
        <div className="nav-bar-right-side-container">
          <NavLink to={`/`} className="icon-wrapper">
            <AiFillHome className="icon-buttons" />
          </NavLink>
          <NewPost />
          <NavLink to={`/explore`} className="icon-wrapper">
            <AiOutlineCompass className="icon-buttons side-step" />
          </NavLink>
          <ProfileDropDownMenu />
        </div>
      </div>
    </div>
  );
};

export default NavBar;

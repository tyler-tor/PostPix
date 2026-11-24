import React, { useEffect } from "react";
import { NavLink } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import { loadSuggestions } from "../../store/users";
import "./SideNonFollow.css";

// "Check out these users": people you do not follow yet.
const SideNonFollowedUsers = () => {
  const dispatch = useDispatch();
  const byId = useSelector((state) => state.users.byId);
  const suggestionIds = useSelector((state) => state.users.suggestionIds);

  useEffect(() => {
    dispatch(loadSuggestions());
  }, [dispatch]);

  return (
    <div className="side-non-follower-list">
      {suggestionIds.map((id) => (
        <div className="each-non-follower" key={id}>
          <img className="non-follower-picture" src={byId[id].profilePicture} alt="" />
          <NavLink to={`/${id}`} className="non-follower-link">
            {byId[id].username}
          </NavLink>
        </div>
      ))}
    </div>
  );
};

export default SideNonFollowedUsers;

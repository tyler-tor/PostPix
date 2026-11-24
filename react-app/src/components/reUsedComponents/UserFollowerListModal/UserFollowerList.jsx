import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { NavLink } from "react-router";
import { getAllFollowers } from "../../../store/follower";
import { getAllFollowing } from "../../../store/following";
import { getProfileFollowing } from "../../../store/profile_following_store";
import { getProfileUser } from "../../../store/profileUser";
import "./UserFollowerList.css";

const UserFollowerList = ({ followers, onClose }) => {
  const dispatch = useDispatch();

  return (
    <div className="user-liked-list">
      <ul>
        {followers.map((user) => {
          return (
            <NavLink to={`/${user.id}`} onClick={() => {
                dispatch(getAllFollowers(user.id))
                dispatch(getAllFollowing(user.id))
                dispatch(getProfileFollowing(user.id))
                dispatch(getProfileUser(user.id))
                onClose()

            }}>
              <li key={user.id}>
                <img src={user.profilePicture} />
                <span>{user.username}</span>
              </li>
            </NavLink>
          );
        })}
      </ul>
    </div>
  );
};

export default UserFollowerList;

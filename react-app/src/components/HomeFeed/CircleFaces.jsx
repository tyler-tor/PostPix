import React, { useEffect } from "react";
import { NavLink } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import { loadFollowing } from "../../store/users";

// Row of avatars: the people you follow.
const CircleFaces = () => {
  const dispatch = useDispatch();
  const byId = useSelector((state) => state.users.byId);
  const followingIds = useSelector((state) => state.users.followingIds);

  useEffect(() => {
    dispatch(loadFollowing());
  }, [dispatch]);

  return (
    <>
      {followingIds.map((id) => {
        const followed = byId[id];
        return (
          <NavLink to={`/${id}`} key={id} className="circle-face-children-containers">
            <img src={followed.profilePicture} alt="" />
            <div>{followed.username}</div>
          </NavLink>
        );
      })}
    </>
  );
};

export default CircleFaces;

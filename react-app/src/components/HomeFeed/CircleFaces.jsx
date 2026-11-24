import React, { useEffect } from "react";
import { NavLink } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import { getAllFollowing } from "../../store/following";

const CircleFaces = () => {
  const dispatch = useDispatch()
  const user = useSelector((state) => state.session.user);
  const following = Object.values(useSelector((state) => state.follow));

  useEffect(() => {
    dispatch(getAllFollowing(user.id))
  }, [dispatch])
  return (
    <>
    {following.map(followed => {
      return (
        <NavLink to={`/${followed.id}`}
        key={followed.id}
        className="circle-face-children-containers">
          <img src={followed.profilePicture} alt="" />
          <div>{followed.username}</div>
        </NavLink>
      )
    })}
    </>
  );
};

export default CircleFaces;

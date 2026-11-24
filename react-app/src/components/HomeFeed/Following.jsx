import React, { useEffect } from "react";
import { Link } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import { loadFollowing } from "../../store/users";
import Avatar from "../ui/Avatar";

// A row of the people you follow: tap a face to open their profile.
const Following = () => {
  const dispatch = useDispatch();
  const byId = useSelector((state) => state.users.byId);
  const followingIds = useSelector((state) => state.users.followingIds);

  useEffect(() => {
    dispatch(loadFollowing());
  }, [dispatch]);

  if (followingIds.length === 0) return null;
  return (
    <section className="following" aria-labelledby="following-title">
      <h2 id="following-title" className="visually-hidden">
        People you follow
      </h2>
      <ul className="following-row">
        {followingIds.map((id) => (
          <li key={id}>
            <Link to={`/${id}`} className="following-item">
              <Avatar src={byId[id].profilePicture} size={3.5} />
              <span>{byId[id].username}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
};

export default Following;

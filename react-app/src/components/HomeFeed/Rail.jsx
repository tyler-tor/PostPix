import React, { useEffect, useState } from "react";
import { Link } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import { FiGithub, FiLinkedin } from "react-icons/fi";
import { loadSuggestions, setFollow } from "../../store/users";
import Avatar from "../ui/Avatar";

const TEAM = [
  { name: "Derek Torrero", linkedin: "https://www.linkedin.com/in/derek-torrero-02823018a/", github: "https://github.com/tyler-tor" },
  { name: "Theo Fandrich", linkedin: "https://www.linkedin.com/in/theofandrich/", github: "https://github.com/theoman42" },
  { name: "Alan Deleon", linkedin: "https://www.linkedin.com/in/alan-de-leon-b54621212/", github: "https://github.com/AlanDeleon88" },
];

const Suggestion = ({ id }) => {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.users.byId[id]);
  const [busy, setBusy] = useState(false);
  return (
    <li className="rail-person">
      <Link to={`/${id}`}>
        <Avatar src={user.profilePicture} size={2.5} />
        <span>
          <strong>{user.username}</strong>
          <span className="rail-sub">{user.firstName} {user.lastName}</span>
        </span>
      </Link>
      <button
        type="button"
        className="btn btn-secondary btn-sm"
        disabled={busy}
        aria-label={`Follow ${user.username}`}
        onClick={async () => {
          setBusy(true);
          await dispatch(setFollow(id, true));
          setBusy(false);
        }}
      >
        Follow
      </button>
    </li>
  );
};

// Right-hand column on wide screens: who you are, who to follow, who built this.
const Rail = () => {
  const dispatch = useDispatch();
  const me = useSelector((state) => state.session.user);
  const suggestionIds = useSelector((state) => state.users.suggestionIds);

  useEffect(() => {
    dispatch(loadSuggestions());
  }, [dispatch]);

  return (
    <aside className="rail" aria-label="Suggestions">
      <Link to={`/${me.id}`} className="rail-me">
        <Avatar src={me.profilePicture} size={3.5} />
        <span>
          <strong>{me.username}</strong>
          <span className="rail-sub">{me.firstName} {me.lastName}</span>
        </span>
      </Link>

      {suggestionIds.length > 0 && (
        <section aria-labelledby="rail-follow">
          <h2 id="rail-follow" className="rail-title">People to follow</h2>
          <ul className="rail-people">
            {suggestionIds.map((id) => (
              <Suggestion key={id} id={id} />
            ))}
          </ul>
        </section>
      )}

      <section aria-labelledby="rail-credits" className="rail-credits">
        <h2 id="rail-credits" className="rail-title">Built by</h2>
        <ul>
          {TEAM.map((person) => (
            <li key={person.name}>
              <span>{person.name}</span>
              <a href={person.github} aria-label={`${person.name} on GitHub`}>
                <FiGithub aria-hidden="true" />
              </a>
              <a href={person.linkedin} aria-label={`${person.name} on LinkedIn`}>
                <FiLinkedin aria-hidden="true" />
              </a>
            </li>
          ))}
        </ul>
      </section>
    </aside>
  );
};

export default Rail;

import React, { useState } from "react";
import { NavLink } from "react-router";
import { Modal } from "../../../context/Modal";
import usePagedList from "../../../hooks/usePagedList";
import LoadMore from "../LoadMore";
import "./UserListModal.css";

// The list inside the modal: loaded when the modal opens, kept only while open.
const UserList = ({ url, dataKey, onClose }) => {
  const { items: users, status, errors, hasMore, loadingMore, loadMore } = usePagedList(url, dataKey);

  return (
    <div className="user-liked-list">
      {status === "loading" && <p>Loading...</p>}
      {status === "error" && <p>{errors[0]}</p>}
      {status === "ready" && users.length === 0 && <p>Nobody yet.</p>}
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            <NavLink to={`/${user.id}`} onClick={onClose}>
              <img src={user.profilePicture} alt="" />
              <span>{user.username}</span>
            </NavLink>
          </li>
        ))}
      </ul>
      <LoadMore hasMore={hasMore} loading={loadingMore} onLoadMore={loadMore} />
    </div>
  );
};

// A button (its content is `children`) that opens a list of users fetched from
// `url`. Used for followers, following and the people who liked a post.
//   dataKey: the key of the array in the JSON ("followers", "following", "user").
const UserListModal = ({ url, dataKey, children, className }) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" className={className || "no-styling-actual"} onClick={() => setOpen(true)}>
        {children}
      </button>
      {open && (
        <Modal onClose={() => setOpen(false)}>
          <UserList url={url} dataKey={dataKey} onClose={() => setOpen(false)} />
        </Modal>
      )}
    </>
  );
};

export default UserListModal;

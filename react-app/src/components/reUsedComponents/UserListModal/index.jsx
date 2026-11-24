import React, { useState } from "react";
import { Link } from "react-router";
import Avatar from "../../ui/Avatar";
import { Modal } from "../../../context/Modal";
import usePagedList from "../../../hooks/usePagedList";
import LoadMore from "../LoadMore";
import "./UserListModal.css";

// The list inside the modal: loaded when the modal opens, kept only while open.
const UserList = ({ url, dataKey, onClose }) => {
  const { items: users, status, errors, hasMore, loadingMore, loadMore } = usePagedList(url, dataKey);

  return (
    <div className="user-list">
      {status === "loading" && <p className="user-list-note" role="status">Loading...</p>}
      {status === "error" && <p className="user-list-note" role="alert">{errors[0]}</p>}
      {status === "ready" && users.length === 0 && <p className="user-list-note">Nobody yet.</p>}
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            <Link to={`/${user.id}`} onClick={onClose}>
              <Avatar src={user.profilePicture} size={2.5} />
              <span>
                <strong>{user.username}</strong>
                {(user.firstName || user.lastName) && (
                  <span className="user-list-name">
                    {user.firstName} {user.lastName}
                  </span>
                )}
              </span>
            </Link>
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
const UserListModal = ({ url, dataKey, title = "People", children, className }) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" className={className || "text-btn"} aria-haspopup="dialog" onClick={() => setOpen(true)}>
        {children}
      </button>
      {open && (
        <Modal title={title} size="sm" onClose={() => setOpen(false)}>
          <UserList url={url} dataKey={dataKey} onClose={() => setOpen(false)} />
        </Modal>
      )}
    </>
  );
};

export default UserListModal;

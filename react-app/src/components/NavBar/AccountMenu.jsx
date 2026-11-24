import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { useDispatch, useSelector } from "react-redux";
import { FiUser, FiLogOut } from "react-icons/fi";
import { logout } from "../../store/session";
import Avatar from "../ui/Avatar";

// Your picture in the nav bar; opens a small menu (Profile, Log out).
// Closes on Escape, on a click elsewhere, or when you pick something.
const AccountMenu = () => {
  const dispatch = useDispatch();
  const user = useSelector((state) => state.session.user);
  const [open, setOpen] = useState(false);
  const root = useRef(null);
  const button = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const outside = (e) => {
      if (root.current && !root.current.contains(e.target)) setOpen(false);
    };
    const escape = (e) => {
      if (e.key === "Escape") {
        setOpen(false);
        button.current?.focus();
      }
    };
    document.addEventListener("click", outside);
    document.addEventListener("keydown", escape);
    return () => {
      document.removeEventListener("click", outside);
      document.removeEventListener("keydown", escape);
    };
  }, [open]);

  return (
    <div className="account" ref={root}>
      <button
        ref={button}
        type="button"
        className="nav-link nav-account"
        aria-label="Account menu"
        aria-expanded={open}
        aria-haspopup="true"
        onClick={() => setOpen((v) => !v)}
      >
        <Avatar src={user.profilePicture} size={1.75} />
        <span className="nav-label">You</span>
      </button>
      {open && (
        <ul className="account-menu">
          <li>
            <Link to={`/${user.id}`} onClick={() => setOpen(false)}>
              <FiUser aria-hidden="true" /> Profile
            </Link>
          </li>
          <li>
            <button type="button" onClick={() => dispatch(logout())}>
              <FiLogOut aria-hidden="true" /> Log out
            </button>
          </li>
        </ul>
      )}
    </div>
  );
};

export default AccountMenu;

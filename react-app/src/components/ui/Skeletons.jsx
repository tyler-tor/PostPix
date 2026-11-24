import React from "react";
import "./ui.css";

// Grey placeholder shapes shown while a page loads, laid out like the real
// thing so the page does not jump. Hidden from screen readers; the wrapper
// announces "Loading" once.
const Wrap = ({ label, children, className }) => (
  <div className={className} role="status" aria-busy="true">
    <span className="visually-hidden">{label}</span>
    <div aria-hidden="true" className="skeleton-wrap">{children}</div>
  </div>
);

export const FeedSkeleton = () => (
  <Wrap label="Loading posts" className="feed-list">
    {[0, 1].map((i) => (
      <div className="feed-post" key={i}>
        <div className="feed-post-head">
          <span className="skeleton" style={{ width: "2.5rem", height: "2.5rem", borderRadius: "var(--radius-avatar)" }} />
          <span className="skeleton" style={{ width: "8rem", height: "1rem" }} />
        </div>
        <div className="skeleton" style={{ aspectRatio: 1, borderRadius: 0 }} />
        <div style={{ padding: "var(--space-4)", display: "grid", gap: "var(--space-2)" }}>
          <span className="skeleton" style={{ width: "5rem", height: "1rem" }} />
          <span className="skeleton" style={{ width: "70%", height: "1rem" }} />
        </div>
      </div>
    ))}
  </Wrap>
);

export const GridSkeleton = ({ count = 12 }) => (
  <Wrap label="Loading posts">
    <ul className="post-grid">
      {Array.from({ length: count }, (_, i) => (
        <li key={i}>
          <span className="skeleton" style={{ display: "block", width: "100%", height: "100%", borderRadius: "var(--radius-md)" }} />
        </li>
      ))}
    </ul>
  </Wrap>
);

export const ProfileSkeleton = () => (
  <Wrap label="Loading profile">
    <div className="profile-head">
      <span className="skeleton" style={{ width: "9rem", height: "9rem", borderRadius: "var(--radius-avatar)" }} />
      <div className="profile-info">
        <span className="skeleton" style={{ width: "12rem", height: "2rem" }} />
        <span className="skeleton" style={{ width: "16rem", height: "1.25rem" }} />
      </div>
    </div>
    <ul className="post-grid">
      {Array.from({ length: 6 }, (_, i) => (
        <li key={i}>
          <span className="skeleton" style={{ display: "block", width: "100%", height: "100%", borderRadius: "var(--radius-md)" }} />
        </li>
      ))}
    </ul>
  </Wrap>
);

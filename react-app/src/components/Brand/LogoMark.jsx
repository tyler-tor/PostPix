import React from "react";

// The Postpix mark: a teal rounded square with a white "P". Same shapes as
// public/favicon.svg. Decorative: the words next to it carry the name.
const LogoMark = ({ className = "" }) => (
  <svg className={className} viewBox="0 0 64 64" aria-hidden="true" focusable="false">
    <rect width="64" height="64" rx="16" fill="var(--logo-bg, #0f766e)" />
    <path
      fill="var(--logo-fg, #fff)"
      fillRule="evenodd"
      d="M17 14H32a15 15 0 0 1 0 30H26v6H17Z M26 23H32a6 6 0 0 1 0 12H26Z"
    />
  </svg>
);

export default LogoMark;

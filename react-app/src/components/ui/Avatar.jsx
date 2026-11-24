import React from "react";

// A rounded-square profile picture. Decorative (alt=""): the person's name is
// always written next to it. size is in rem.
const Avatar = ({ src, size = 2.5, className = "" }) => (
  <img
    className={`avatar ${className}`.trim()}
    src={src}
    alt=""
    loading="lazy"
    decoding="async"
    style={{ "--avatar-size": `${size}rem` }}
  />
);

export default Avatar;

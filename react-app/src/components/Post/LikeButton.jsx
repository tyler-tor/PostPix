import React from "react";
import { useDispatch } from "react-redux";
import { FiHeart } from "react-icons/fi";
import { toggleLike } from "../../store/posts";

// The heart. A toggle button: screen readers hear "Like, pressed" when liked.
const LikeButton = ({ post }) => {
  const dispatch = useDispatch();
  return (
    <button
      type="button"
      className={`like-btn${post.likedByMe ? " is-liked" : ""}`}
      aria-pressed={post.likedByMe}
      aria-label="Like"
      onClick={() => dispatch(toggleLike(post.id))}
    >
      <FiHeart aria-hidden="true" />
    </button>
  );
};

export default LikeButton;

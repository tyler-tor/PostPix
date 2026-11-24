import React, { useState } from "react";
import { useSelector } from "react-redux";
import { FiHeart, FiMessageCircle } from "react-icons/fi";
import PostDetail from "./PostDetail";
import "./PostTile.css";

// A square photo in a grid. It is a button: Enter or Space opens the post.
// Likes and comments show on hover and on keyboard focus.
// `featured` tiles are drawn twice as big and use the full-size picture.
const PostTile = ({ postId, featured = false }) => {
  const [open, setOpen] = useState(false);
  const post = useSelector((state) => state.posts.byId[postId]);
  if (!post) return null;

  const description = post.caption || `Photo by ${post.users.username}`;
  return (
    <>
      <button
        type="button"
        className={`tile${featured ? " tile-featured" : ""}`}
        data-tile
        aria-haspopup="dialog"
        aria-label={`${description}. ${post.likes} likes, ${post.commentCount} comments.`}
        onClick={() => setOpen(true)}
      >
        <img
          src={featured ? post.imgUrl : post.thumbUrl || post.imgUrl}
          alt=""
          loading="lazy"
          decoding="async"
        />
        <span className="tile-meta" aria-hidden="true">
          <span>
            <FiHeart /> {post.likes}
          </span>
          <span>
            <FiMessageCircle /> {post.commentCount}
          </span>
        </span>
      </button>
      {open && <PostDetail postId={postId} onClose={() => setOpen(false)} />}
    </>
  );
};

export default PostTile;

import React, { useState } from "react";
import { Link } from "react-router";
import { useSelector } from "react-redux";
import { FiMessageCircle } from "react-icons/fi";
import Avatar from "../ui/Avatar";
import Time from "../ui/Time";
import LikeButton from "../Post/LikeButton";
import PostOptions from "../Post/PostOptions";
import PostDetail from "../Post/PostDetail";

// The photo frame follows the photo's own shape, but never taller than 4:5 nor
// wider than 3:2, so one huge panorama or tall screenshot cannot take over the feed.
const frameRatio = (post) => {
  if (!post.imgWidth || !post.imgHeight) return 1;
  return Math.min(1.5, Math.max(0.8, post.imgWidth / post.imgHeight));
};

const FeedPost = ({ postId, priority = false }) => {
  const [open, setOpen] = useState(false);
  const post = useSelector((state) => state.posts.byId[postId]);
  const me = useSelector((state) => state.session.user);
  if (!post) return null;
  const author = post.users;

  return (
    <article className="feed-post" aria-label={`Post by ${author.username}`}>
      <header className="feed-post-head">
        <Link to={`/${author.userId}`} className="feed-author">
          <Avatar src={author.profilePicture} size={2.5} />
          <span>
            <strong>{author.username}</strong>
            <Time iso={post.createdAt} className="feed-date" />
          </span>
        </Link>
        {me.id === post.userId && <PostOptions postId={post.id} />}
      </header>

      <div className="feed-photo" style={{ aspectRatio: frameRatio(post) }}>
        <img
          src={post.imgUrl}
          alt={post.caption || `Photo by ${author.username}`}
          width={post.imgWidth || undefined}
          height={post.imgHeight || undefined}
          loading={priority ? "eager" : "lazy"}
          decoding="async"
        />
      </div>

      <div className="feed-actions">
        <LikeButton post={post} />
        <button type="button" className="icon-btn" aria-label="Comments" aria-haspopup="dialog" onClick={() => setOpen(true)}>
          <FiMessageCircle aria-hidden="true" />
        </button>
        <span className="feed-likes">
          <strong>{post.likes}</strong> {post.likes === 1 ? "like" : "likes"}
        </span>
      </div>

      {post.caption && (
        <p className="feed-caption">
          <Link to={`/${author.userId}`}>
            <strong>{author.username}</strong>
          </Link>{" "}
          {post.caption}
        </p>
      )}
      <button type="button" className="feed-comments-link" aria-haspopup="dialog" onClick={() => setOpen(true)}>
        {post.commentCount > 0 ? `View ${post.commentCount === 1 ? "1 comment" : `all ${post.commentCount} comments`}` : "Add a comment"}
      </button>
      {open && <PostDetail postId={postId} onClose={() => setOpen(false)} />}
    </article>
  );
};

export default FeedPost;

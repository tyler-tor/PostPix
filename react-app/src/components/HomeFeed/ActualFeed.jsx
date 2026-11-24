import React, { useEffect } from "react";
import { AiOutlineHeart, AiFillHeart } from "react-icons/ai";
import { FaUserCircle } from "react-icons/fa";
import { NavLink } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import PostSettingsModal from "./PostSettingsModal";
import { loadHomeFeed, loadMoreFeed } from "../../store/feeds";
import LoadMore from "../reUsedComponents/LoadMore";
import { toggleLike } from "../../store/posts";
import formatDate from "../../utils/formatDate";

const FeedPost = ({ postId }) => {
  const dispatch = useDispatch();
  const post = useSelector((state) => state.posts.byId[postId]);
  if (!post) return null;

  return (
    <div className="feed-container">
      <div className="feed-child post-username-and-settings-container">
        <div className="poster-username-and-circle">
          <FaUserCircle className="poster-profile-picture-for-post" />
          <NavLink to={`/${post.users.userId}`} className="poster-username">
            <strong className="username-text">{post.users.username}</strong>
          </NavLink>
        </div>
        <PostSettingsModal post={post} />
      </div>
      <div id="post-image" className="feed-child post-image-wrapper">
        <img
          className="feed-child post-image-wrapper"
          src={post.imgUrl}
          loading="lazy"
          decoding="async"
          width={post.imgWidth || undefined}
          height={post.imgHeight || undefined}
          alt={post.caption || `Post by ${post.users.username}`}
        />
      </div>
      <div className="feed-child like-comment-icon-container">
        <button
          type="button"
          className="no-styling"
          onClick={() => dispatch(toggleLike(post.id))}
          aria-pressed={post.likedByMe}
          aria-label={post.likedByMe ? "Unlike" : "Like"}
        >
          {post.likedByMe ? (
            <AiFillHeart className="post-modal-icons-likes-comments no-left-padding red" />
          ) : (
            <AiOutlineHeart className="post-modal-icons-likes-comments no-left-padding" />
          )}
        </button>
      </div>
      <div className="feed-child likes-count-container">
        <strong>{post.likes} likes </strong>
      </div>
      <div className="post-caption-container-and-show-all-comments">
        <div className="username-caption-div">
          <NavLink to={`/${post.users.userId}`} className="username-no-spacing">
            {post.users.username}
          </NavLink>
          <span className="caption-spacing-from-username">{post.caption}</span>
        </div>
      </div>
      <div className="feed-child post-time-passed-container">
        <span className="secondary-text-grey font-size-10">{formatDate(post.createdAt)}</span>
      </div>
    </div>
  );
};

const ActualFeed = () => {
  const dispatch = useDispatch();
  const { ids, nextCursor, loadingMore } = useSelector((state) => state.feeds.home);

  useEffect(() => {
    dispatch(loadHomeFeed());
  }, [dispatch]);

  return (
    <div>
      {ids.map((id) => (
        <FeedPost key={id} postId={id} />
      ))}
      <LoadMore
        hasMore={!!nextCursor}
        loading={loadingMore}
        onLoadMore={() => dispatch(loadMoreFeed("home"))}
        label="Load more posts"
      />
    </div>
  );
};

export default ActualFeed;

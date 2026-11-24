import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { useDispatch, useSelector } from "react-redux";
import { FiX, FiMessageCircle } from "react-icons/fi";
import { Modal } from "../../context/Modal";
import { loadComments, loadMoreComments, addComment } from "../../store/comments";
import Avatar from "../ui/Avatar";
import Time from "../ui/Time";
import LikeButton from "./LikeButton";
import PostOptions from "./PostOptions";
import CommentOptions from "./CommentOptions";
import UserListModal from "../reUsedComponents/UserListModal";
import LoadMore from "../reUsedComponents/LoadMore";
import "./PostDetail.css";

// One post in a dialog: the photo on the left (shown whole, never cropped),
// and on the right who posted it, the caption, the comments, like button and
// a box to write a comment. On a phone the photo is on top and fills the width.
const PostDetail = ({ postId, onClose }) => {
  const dispatch = useDispatch();
  const post = useSelector((state) => state.posts.byId[postId]);
  const me = useSelector((state) => state.session.user);
  const { status, ids, byId, nextCursor, loadingMore } = useSelector((state) => state.comments);
  const [text, setText] = useState("");
  const [errors, setErrors] = useState([]);
  const [busy, setBusy] = useState(false);
  const composer = useRef(null);

  useEffect(() => {
    dispatch(loadComments(postId));
  }, [dispatch, postId]);

  if (!post) return null; // deleted while open: the dialog goes away with it
  const author = post.users;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    const result = await dispatch(addComment(postId, text));
    setBusy(false);
    if (result) {
      setErrors(result);
    } else {
      setText("");
      setErrors([]);
    }
  };

  return (
    <Modal label={`Post by ${author.username}`} size="lg" bare onClose={onClose}>
      <div className="pd">
        <div className="pd-photo">
          <img src={post.imgUrl} alt={post.caption || `Photo by ${author.username}`} decoding="async" />
        </div>

        <div className="pd-side">
          <header className="pd-head">
            <Link to={`/${author.userId}`} className="pd-author" onClick={onClose}>
              <Avatar src={author.profilePicture} size={2.5} />
              <span>
                <strong>{author.username}</strong>
                <Time iso={post.createdAt} className="pd-date" />
              </span>
            </Link>
            {me.id === post.userId && <PostOptions postId={post.id} />}
            <button type="button" className="icon-btn" aria-label="Close post" onClick={onClose}>
              <FiX aria-hidden="true" />
            </button>
          </header>

          <div className="pd-scroll">
            <p className="pd-caption">
              <strong>{author.username}</strong> {post.caption}
            </p>
            <h2 className="visually-hidden">Comments</h2>
            {status === "loading" && ids.length === 0 && <p className="pd-note" role="status">Loading comments...</p>}
            {status === "error" && <p className="pd-note" role="alert">
                Could not load comments.{" "}
                <button type="button" className="text-btn pd-retry" onClick={() => dispatch(loadComments(postId))}>Try again</button>
              </p>}
            {status === "ready" && ids.length === 0 && <p className="pd-note">No comments yet. Be the first.</p>}
            <ul className="pd-comments">
              {ids.map((id) => {
                const comment = byId[id];
                return (
                  <li key={id} className="pd-comment">
                    <Link to={`/${comment.users.id}`} onClick={onClose} aria-label={`${comment.users.username}'s profile`}>
                      <Avatar src={comment.users.profilePicture} size={2} />
                    </Link>
                    <p>
                      <Link to={`/${comment.users.id}`} onClick={onClose}>
                        <strong>{comment.users.username}</strong>
                      </Link>{" "}
                      {comment.body}
                    </p>
                    {comment.myComment && <CommentOptions commentId={id} />}
                  </li>
                );
              })}
            </ul>
            <LoadMore hasMore={!!nextCursor} loading={loadingMore} onLoadMore={() => dispatch(loadMoreComments())} label="Load more comments" />
          </div>

          <div className="pd-foot">
            <div className="pd-actions">
              <LikeButton post={post} />
              <button type="button" className="icon-btn" aria-label="Write a comment" onClick={() => composer.current?.focus()}>
                <FiMessageCircle aria-hidden="true" />
              </button>
              <UserListModal url={`/api/posts/${post.id}/likes/users`} dataKey="user" title="Liked by" className="pd-likes">
                <strong>{post.likes}</strong> {post.likes === 1 ? "like" : "likes"}
              </UserListModal>
            </div>
            <form className="pd-compose" onSubmit={submit} noValidate>
              <label htmlFor={`comment-${postId}`} className="visually-hidden">
                Add a comment
              </label>
              <input
                id={`comment-${postId}`}
                ref={composer}
                className="input"
                type="text"
                placeholder="Add a comment..."
                maxLength={255}
                value={text}
                onChange={(e) => setText(e.target.value)}
                autoComplete="off"
              />
              <button type="submit" className="btn btn-primary btn-sm" disabled={busy || !text.trim()}>
                Post
              </button>
            </form>
            {errors.length > 0 && (
              <ul className="form-errors" role="alert">
                {errors.map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default PostDetail;

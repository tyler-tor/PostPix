import React, { useState } from "react";
import { NavLink } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import { AiOutlineHeart, AiFillHeart } from "react-icons/ai";
import { Modal } from "../../context/Modal";
import { toggleLike } from "../../store/posts";
import { addComment } from "../../store/comments";
import EditCaptionThreeDotsModal from "./EditCaptionSettingsModal";
import UserListModal from "./UserListModal";
import CommentContainer from "./CommentContainer";
import formatDate from "../../utils/formatDate";
import "./SinglePostModal.css";

// A post thumbnail that opens the full post (image, comments, likes) in a modal.
// It only needs the post id: the post itself, including whether you liked it,
// comes from the store, so a grid of 50 tiles makes no extra requests.
const SinglePostModal = ({ postId }) => {
  const [showModal, setShowModal] = useState(false);
  const [comment, setComment] = useState("");
  const [commentErrors, setCommentErrors] = useState([]);
  const dispatch = useDispatch();
  const user = useSelector((state) => state.session.user);
  const post = useSelector((state) => state.posts.byId[postId]);

  if (!post) return null;
  const myPost = user.id === post.userId;

  const submitComment = async (e) => {
    e.preventDefault();
    const errors = await dispatch(addComment(post.id, comment));
    if (errors) {
      setCommentErrors(errors);
    } else {
      setComment("");
      setCommentErrors([]);
    }
  };

  return (
    <>
      {/* The grid shows the small version; the modal below loads the full image. */}
      <img
        src={post.thumbUrl || post.imgUrl}
        alt={post.caption || `Post by ${post.users.username}`}
        loading="lazy"
        decoding="async"
        onClick={() => setShowModal(true)}
      />
      {showModal && (
        <Modal onClose={() => setShowModal(false)}>
          <div className="post-modal-container">
            <div className="post-modal-image-wrapper">
              <img src={post.imgUrl} alt={post.caption || `Post by ${post.users.username}`} decoding="async" />
            </div>
            <div className="post-modal-content-container">
              <div className="post-modal-username-picture-row">
                <div className="post-modal-content-container-image-wrapper">
                  <img src={post.users.profilePicture} alt="" />
                </div>
                <NavLink
                  to={`/${post.users.userId}`}
                  onClick={() => setShowModal(false)}
                  className="username-styling-in-post-modal"
                >
                  <strong>{post.users.username}</strong>
                </NavLink>
                <div className="post-modal-content-container-caption">
                  {myPost && <EditCaptionThreeDotsModal postId={post.id} />}
                </div>
              </div>

              <div className="post-modal-comments-section">
                <CommentContainer postId={post.id} />
              </div>
              <div className="post-modal-like-comment-icon">
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
              <div className="post-modal-likes-count">
                <UserListModal url={`/api/posts/${post.id}/likes/users`} dataKey="user">
                  {post.likes} likes
                </UserListModal>
              </div>
              <div className="post-modal-date-posted">{formatDate(post.createdAt)}</div>
              <div className="post-modal-add-comment-container">
                <div className="left-hand-container-for-post-modal-comment-input">
                  <form className="comment-form-wrapper" onSubmit={submitComment}>
                    <div className="comment-form-container">
                      <input
                        type="text"
                        placeholder="Add a comment..."
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        className="comment-input-styling"
                      />
                      <div className="right-hand-container-for-post-modal-comment-input">
                        <button type="submit">Post</button>
                      </div>
                    </div>
                    {commentErrors.map((error) => (
                      <div key={error}>{error}</div>
                    ))}
                  </form>
                </div>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
};

export default SinglePostModal;

import { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { loadComments, loadMoreComments } from "../../../store/comments";
import LoadMore from "../LoadMore";
import CommentSettingsModal from "../EditCommentModal";

// Caption plus comments of one post. Comments are fetched when this mounts,
// which is when the post modal opens.
const CommentContainer = ({ postId }) => {
  const dispatch = useDispatch();
  const post = useSelector((state) => state.posts.byId[postId]);
  const { status, ids, byId, nextCursor, loadingMore } = useSelector((state) => state.comments);

  useEffect(() => {
    dispatch(loadComments(postId));
  }, [dispatch, postId]);

  return (
    <ul className="comments-section-container">
      <li className="comments-section-child-container">
        <img src={post.users.profilePicture} alt="" />
        <div className="username-styling-in-post-modal">
          <strong>{post.users.username} </strong>
          <span className="body-styling-in-post-modal">{post.caption}</span>
        </div>
      </li>
      {status === "loading" && ids.length === 0 && <li>Loading comments...</li>}
      {status === "error" && <li>Could not load comments.</li>}
      {ids.map((id) => {
        const comment = byId[id];
        return (
          <li className="comments-section-child-container" key={id}>
            <img src={comment.users.profilePicture} alt="" />
            <div className="username-styling-in-post-modal">
              <strong>{comment.users.username} </strong>
              <span className="body-styling-in-post-modal">{comment.body}</span>
            </div>
            {comment.myComment && <CommentSettingsModal commentId={id} />}
          </li>
        );
      })}
      <li>
        <LoadMore
          hasMore={!!nextCursor}
          loading={loadingMore}
          onLoadMore={() => dispatch(loadMoreComments())}
          label="Load more comments"
        />
      </li>
    </ul>
  );
};

export default CommentContainer;

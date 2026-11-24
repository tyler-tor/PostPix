import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { editComment, deleteComment } from "../../store/comments";

const EditCommentForm = ({ onClose, commentId }) => {
  const [errors, setErrors] = useState([]);
  const comment = useSelector((state) => state.comments.byId[commentId]);
  const [body, setBody] = useState(comment?.body ?? "");
  const dispatch = useDispatch();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(editComment(commentId, body));
    if (result) setErrors(result);
    else onClose();
  };

  const destroyComment = async (e) => {
    e.preventDefault();
    const result = await dispatch(deleteComment(commentId));
    if (result) setErrors(result);
  };

  return (
    <div className="post-form-wrapper">
      <form onSubmit={handleSubmit} className="post-form-container">
        <ul>
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
        <div className="post-form-children">
          <input
            type="text"
            placeholder="comment"
            required
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
        </div>
        <div className="post-form-children">
          <button className="same-button" type="submit">
            Submit
          </button>
        </div>
      </form>
      <button onClick={destroyComment} className="modal-delete-buttons">
        Delete
      </button>
    </div>
  );
};

export default EditCommentForm;

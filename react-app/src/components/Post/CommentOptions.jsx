import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { FiMoreHorizontal } from "react-icons/fi";
import { Modal } from "../../context/Modal";
import { editComment, deleteComment } from "../../store/comments";

// The "..." on your own comment: edit its text or delete it.
const CommentOptions = ({ commentId }) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" className="icon-btn icon-btn-sm" aria-label="Comment options" aria-haspopup="dialog" onClick={() => setOpen(true)}>
        <FiMoreHorizontal aria-hidden="true" />
      </button>
      {open && <CommentDialog commentId={commentId} onClose={() => setOpen(false)} />}
    </>
  );
};

const CommentDialog = ({ commentId, onClose }) => {
  const dispatch = useDispatch();
  const comment = useSelector((state) => state.comments.byId[commentId]);
  const [body, setBody] = useState(comment?.body ?? "");
  const [errors, setErrors] = useState([]);
  const [busy, setBusy] = useState(false);

  const save = async (e) => {
    e.preventDefault();
    setBusy(true);
    const result = await dispatch(editComment(commentId, body));
    setBusy(false);
    if (result) setErrors(result);
    else onClose();
  };

  const remove = async () => {
    setBusy(true);
    const result = await dispatch(deleteComment(commentId));
    if (result) {
      setBusy(false);
      setErrors(result);
    }
  };

  return (
    <Modal title="Edit comment" size="sm" onClose={onClose}>
      <form className="dialog-stack" onSubmit={save} noValidate>
        {errors.length > 0 && (
          <ul className="form-errors" role="alert">
            {errors.map((error) => (
              <li key={error}>{error}</li>
            ))}
          </ul>
        )}
        <div className="field">
          <label htmlFor="edit-comment">Comment</label>
          <textarea id="edit-comment" className="input" maxLength={255} value={body} onChange={(e) => setBody(e.target.value)} autoFocus />
        </div>
        <div className="dialog-actions">
          <button type="button" className="btn btn-secondary danger-text" onClick={remove} disabled={busy}>
            Delete
          </button>
          <button type="submit" className="btn btn-primary" disabled={busy || !body.trim()}>
            Save
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default CommentOptions;

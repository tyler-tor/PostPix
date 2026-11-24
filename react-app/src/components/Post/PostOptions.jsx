import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { FiMoreHorizontal } from "react-icons/fi";
import { Modal } from "../../context/Modal";
import { editCaption, deletePost } from "../../store/posts";

const MAX_CAPTION = 150;

// The "..." button on your own post and the dialog it opens:
// a short menu -> edit the caption, or confirm deleting the post.
const PostOptions = ({ postId }) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" className="icon-btn" aria-label="Post options" aria-haspopup="dialog" onClick={() => setOpen(true)}>
        <FiMoreHorizontal aria-hidden="true" />
      </button>
      {open && <PostOptionsDialog postId={postId} onClose={() => setOpen(false)} />}
    </>
  );
};

const PostOptionsDialog = ({ postId, onClose }) => {
  const [view, setView] = useState("menu"); // menu | edit | delete
  const titles = { menu: "Post options", edit: "Edit caption", delete: "Delete this post?" };
  return (
    <Modal title={titles[view]} size="sm" onClose={onClose}>
      {view === "menu" && (
        <div className="dialog-stack">
          <button type="button" className="btn btn-secondary btn-block" onClick={() => setView("edit")}>
            Edit caption
          </button>
          <button type="button" className="btn btn-secondary btn-block danger-text" onClick={() => setView("delete")}>
            Delete post
          </button>
          <button type="button" className="btn btn-ghost btn-block" onClick={onClose}>
            Cancel
          </button>
        </div>
      )}
      {view === "edit" && <EditCaption postId={postId} onDone={onClose} onBack={() => setView("menu")} />}
      {view === "delete" && <ConfirmDelete postId={postId} onBack={() => setView("menu")} />}
    </Modal>
  );
};

const EditCaption = ({ postId, onDone, onBack }) => {
  const dispatch = useDispatch();
  const current = useSelector((state) => state.posts.byId[postId]?.caption ?? "");
  const [caption, setCaption] = useState(current);
  const [errors, setErrors] = useState([]);
  const [busy, setBusy] = useState(false);

  const save = async (e) => {
    e.preventDefault();
    setBusy(true);
    const result = await dispatch(editCaption(postId, caption));
    setBusy(false);
    if (result) setErrors(result);
    else onDone();
  };

  return (
    <form className="dialog-stack" onSubmit={save} noValidate>
      {errors.length > 0 && (
        <ul className="form-errors" role="alert">
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}
      <div className="field">
        <label htmlFor="edit-caption">Caption</label>
        <textarea
          id="edit-caption"
          className="input"
          maxLength={MAX_CAPTION}
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
          autoFocus
        />
        <span className="field-hint">
          {caption.length}/{MAX_CAPTION}
        </span>
      </div>
      <div className="dialog-actions">
        <button type="button" className="btn btn-ghost" onClick={onBack}>
          Back
        </button>
        <button type="submit" className="btn btn-primary" disabled={busy || !caption.trim()}>
          Save
        </button>
      </div>
    </form>
  );
};

const ConfirmDelete = ({ postId, onBack }) => {
  const dispatch = useDispatch();
  const [errors, setErrors] = useState([]);
  const [busy, setBusy] = useState(false);

  const remove = async () => {
    setBusy(true);
    const result = await dispatch(deletePost(postId));
    if (result) {
      setBusy(false);
      setErrors(result);
    } // on success the post disappears and this dialog goes with it
  };

  return (
    <div className="dialog-stack">
      <p>This also deletes its comments and likes. You cannot undo it.</p>
      {errors.length > 0 && (
        <ul className="form-errors" role="alert">
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}
      <div className="dialog-actions">
        <button type="button" className="btn btn-secondary" onClick={onBack} autoFocus>
          Cancel
        </button>
        <button type="button" className="btn btn-danger" onClick={remove} disabled={busy}>
          Delete post
        </button>
      </div>
    </div>
  );
};

export default PostOptions;

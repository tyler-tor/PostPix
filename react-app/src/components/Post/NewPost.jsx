import React, { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router";
import { FiPlus, FiImage } from "react-icons/fi";
import { Modal } from "../../context/Modal";
import { createPost } from "../../store/posts";
import { api } from "../../utils/api";

const MAX_CAPTION = 150;

// The "New post" button and its dialog: choose a photo (it uploads as soon as
// it is chosen), write a caption, share.
const NewPost = ({ className = "", children }) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" className={className} data-new-post aria-haspopup="dialog" onClick={() => setOpen(true)}>
        {children || (
          <>
            <FiPlus aria-hidden="true" />
            <span>New post</span>
          </>
        )}
      </button>
      {open && (
        <Modal title="New post" onClose={() => setOpen(false)}>
          <NewPostForm onDone={() => setOpen(false)} />
        </Modal>
      )}
    </>
  );
};

const NewPostForm = ({ onDone }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const user = useSelector((state) => state.session.user);
  const [caption, setCaption] = useState("");
  const [preview, setPreview] = useState("");
  const [upload, setUpload] = useState({ status: "idle", image: null }); // idle | uploading | done | error
  const [errors, setErrors] = useState([]);
  const [busy, setBusy] = useState(false);
  const previewRef = useRef("");

  useEffect(() => () => previewRef.current && URL.revokeObjectURL(previewRef.current), []);

  const choose = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    previewRef.current = URL.createObjectURL(file);
    setPreview(previewRef.current);
    setErrors([]);
    setUpload({ status: "uploading", image: null });
    const form = new FormData();
    form.append("image", file);
    const res = await api("/api/img/upload", { method: "POST", form });
    if (res.ok) setUpload({ status: "done", image: res.data });
    else {
      setUpload({ status: "error", image: null });
      setErrors(res.errors);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!upload.image) {
      setErrors(["Choose a photo first."]);
      return;
    }
    setBusy(true);
    const { url, thumbUrl, width, height } = upload.image;
    const result = await dispatch(createPost({ caption, imgUrl: url, thumbUrl, width, height }));
    setBusy(false);
    if (result) {
      setErrors(result);
    } else {
      onDone();
      navigate(`/${user.id}`);
    }
  };

  return (
    <form className="dialog-stack" onSubmit={submit} noValidate>
      {errors.length > 0 && (
        <ul className="form-errors" role="alert">
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}
      <div className="field">
        <label htmlFor="new-post-photo" className="photo-drop">
          {preview ? (
            <img src={preview} alt="Preview of the photo you chose" />
          ) : (
            <span className="photo-drop-empty">
              <FiImage aria-hidden="true" />
              <strong>Choose a photo</strong>
              <span>JPEG, PNG, WebP or GIF, up to 10 MB</span>
            </span>
          )}
        </label>
        <input
          id="new-post-photo"
          className="visually-hidden-input"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={choose}
          autoFocus
        />
        <span className="field-hint" role="status">
          {upload.status === "uploading" && "Uploading..."}
          {upload.status === "done" && "Photo ready."}
        </span>
      </div>
      <div className="field">
        <label htmlFor="new-post-caption">Caption</label>
        <textarea
          id="new-post-caption"
          className="input"
          maxLength={MAX_CAPTION}
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
        />
        <span className="field-hint">
          {caption.length}/{MAX_CAPTION}
        </span>
      </div>
      <div className="dialog-actions">
        <button type="submit" className="btn btn-primary" disabled={busy || upload.status !== "done" || !caption.trim()}>
          Share
        </button>
      </div>
    </form>
  );
};

export default NewPost;

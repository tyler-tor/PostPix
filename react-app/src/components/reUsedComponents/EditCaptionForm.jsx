import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { editCaption } from "../../store/posts";

const EditCaptionForm = ({ onClose, postId }) => {
  const [errors, setErrors] = useState([]);
  const current = useSelector((state) => state.posts.byId[postId]?.caption ?? "");
  const [caption, setCaption] = useState(current);
  const dispatch = useDispatch();

  const onCaptionSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(editCaption(postId, caption));
    if (result) setErrors(result);
    else onClose();
  };

  return (
    <div className="post-form-wrapper">
      <form className="post-form-container" onSubmit={onCaptionSubmit}>
        <div>
          {errors.map((error) => (
            <div key={error}>{error}</div>
          ))}
        </div>
        <div className="post-form-children">
          <input
            name="caption"
            type="text"
            placeholder="Caption"
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
          />
        </div>
        <div className="post-form-children">
          <button className="post-form-default-submit-button" type="submit">
            Submit
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditCaptionForm;

import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router";
import { createPost } from "../../store/posts";
import ImageUploadComponent from "./ImageUploadComponent";
import './NavBar.css'

const PostForm = ({ onClose }) => {
  const [errors, setErrors] = useState([]);
  const [caption, setCaption] = useState("");
  const [url, setUrl] = useState("");
  const user = useSelector((state) => state.session.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const onPostSubmit = async (e) => {
    e.preventDefault();
    if (!url) {
      setErrors(["Upload an image first."]);
      return;
    }
    const result = await dispatch(createPost({ caption, imgUrl: url }));
    if (result) {
      setErrors(result);
    } else {
      navigate(`/${user.id}`);
      onClose();
    }
  };

  return (
    <div className="post-form-wrapper">
      <ImageUploadComponent setUrl={setUrl} />
      <form className="post-form-container" onSubmit={onPostSubmit}>
        <div>
          {errors.map((error) => (
            <div key={error}>{error}</div>
          ))}
        </div>
        <div className="post-form-children">
          <input
            className="post-form-input-text-boxes"
            name="caption"
            type="text"
            placeholder="Caption"
            value={caption}
            onChange={(e) => setCaption(e.target.value)}
          />
        </div>
        <div className="post-form-children">
          <button className="post-form-default-submit-button" type="submit">
            Post
          </button>
        </div>
      </form>
    </div>
  );
};

export default PostForm;

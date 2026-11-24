import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router";
import { createPost } from "../../store/posts";
import ImageUploadComponent from "./ImageUploadComponent";
import './NavBar.css'

const PostForm = ({ onClose }) => {
  const [errors, setErrors] = useState([]);
  const [caption, setCaption] = useState("");
  const [image, setImage] = useState(null); // { url, thumbUrl, width, height } from the upload
  const user = useSelector((state) => state.session.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const onPostSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setErrors(["Upload an image first."]);
      return;
    }
    const result = await dispatch(createPost({ caption, imgUrl: image.url, thumbUrl: image.thumbUrl, width: image.width, height: image.height }));
    if (result) {
      setErrors(result);
    } else {
      navigate(`/${user.id}`);
      onClose();
    }
  };

  return (
    <div className="post-form-wrapper">
      <ImageUploadComponent onUploaded={setImage} />
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

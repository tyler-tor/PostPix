import { useState } from "react";
import { useDispatch } from "react-redux";
import { deletePost } from "../../../store/posts";

const DeletePost = ({ onClose, postId }) => {
  const dispatch = useDispatch();
  const [errors, setErrors] = useState([]);

  const handleYes = async (e) => {
    e.preventDefault();
    const result = await dispatch(deletePost(postId));
    if (result) setErrors(result);
  };

  return (
    <div className="delete-post-container">
      <div>Are you sure you want to delete the post?</div>
      {errors.map((error) => (
        <div key={error}>{error}</div>
      ))}
      <div className="delete-post-button-container">
        <button onClick={handleYes}>Yes</button>
        <button
          onClick={(e) => {
            e.preventDefault();
            onClose();
          }}
        >
          No
        </button>
      </div>
    </div>
  );
};

export default DeletePost;

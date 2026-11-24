import { useDispatch } from "react-redux";
import { deletePost } from "../../../store/post";

const DeletePost = ({ onClose, postId }) => {
  const dispatch = useDispatch();

  const handleYes = async (e) => {
    e.preventDefault();
    const del = await dispatch(deletePost(postId.postId)).then(() => {
      //!commented this out because it seemed it was causing a memory leak.
      //!model still closes even though it is commented out.
    });
  };

  const handleNo = (e) => {
    e.preventDefault();
    onClose();
  };

  return (
    <>
      <div className="delete-post-container">
        <div>Are you sure you want to delete the post?</div>
        <div className="delete-post-button-container">
          <button onClick={handleYes}>Yes</button>
          <button onClick={handleNo}>No</button>
        </div>
      </div>
    </>
  );
};

export default DeletePost;

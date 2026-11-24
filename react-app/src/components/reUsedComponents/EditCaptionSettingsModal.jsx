import React, { useState } from "react";
import { Modal } from "../../context/Modal";
import { TbDots } from "react-icons/tb";
import EditCaptionFormModal from "./EditCaptionModal";
import DeletePostModal from "./DeletePostModal";

// The "..." menu on your own post: edit the caption or delete the post.
const EditCaptionThreeDotsModal = ({ postId }) => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <a onClick={() => setShowModal(true)}>
        <TbDots className="the-three-dots" />
      </a>
      {showModal && (
        <Modal onClose={() => setShowModal(false)}>
          <div className="post-settings-modal-container-new">
            <EditCaptionFormModal postId={postId} onClose={() => setShowModal(false)} />
            <DeletePostModal postId={postId} />
          </div>
        </Modal>
      )}
    </>
  );
};

export default EditCaptionThreeDotsModal;

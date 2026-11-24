import React, { useState } from "react";
import { Modal } from "../../context/Modal";
import { TbDots } from "react-icons/tb";
import EditCommentForm from "./EditCommentForm";

const CommentSettingsModal = ({ commentId }) => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <a onClick={() => setShowModal(true)}>
        <TbDots className="the-three-dots" />
      </a>
      {showModal && (
        <Modal onClose={() => setShowModal(false)}>
          <EditCommentForm commentId={commentId} onClose={() => setShowModal(false)} />
        </Modal>
      )}
    </>
  );
};

export default CommentSettingsModal;

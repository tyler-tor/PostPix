import React, { useState } from "react";
import { Modal } from "../../context/Modal";
import SignUpForm from "./SignUpForm";
import "./LoginPage.css";

const SignUpFormModal = () => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <button type="button" className="link-button" data-signup onClick={() => setShowModal(true)}>
        Sign up
      </button>
      {showModal && (
        <Modal title="Create your account" size="md" onClose={() => setShowModal(false)}>
          <SignUpForm onClose={() => setShowModal(false)} />
        </Modal>
      )}
    </>
  );
};

export default SignUpFormModal;

import React from "react";
import LoginForm from "./LoginForm";
import SignUpFormModal from "./SignUpModal";
import Wordmark from "../Brand/Wordmark";
import Mosaic from "../Brand/Mosaic";
import "./LoginPage.css";

// Logged-out home. Two halves on a wide screen: a deep-teal brand panel with a
// wall of tinted tiles, and the log-in form. On a phone they stack.
const LoginPage = () => (
  <div className="auth">
    <section className="auth-hero" aria-labelledby="auth-headline">
      <Wordmark size="lg" tone="light" />
      <div className="auth-hero-copy">
        <h1 id="auth-headline">Share photos with friends.</h1>
        <p>Post a picture, follow people you like, and say something nice in the comments.</p>
      </div>
      <Mosaic />
    </section>

    <section className="auth-panel" aria-labelledby="auth-title">
      <div className="auth-card">
        <LoginForm />
        <p className="auth-switch">
          New to Postpix? <SignUpFormModal />
        </p>
        <p className="demo-note">
          Postpix is a portfolio demo project. It is not affiliated with any other social network.
          Please don't reuse a real password here.
        </p>
      </div>
    </section>
  </div>
);

export default LoginPage;

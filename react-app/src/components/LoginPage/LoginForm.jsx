import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Navigate } from "react-router";
import { login } from "../../store/session";
import Wordmark from "../Brand/Wordmark";

const LoginForm = () => {
  const [errors, setErrors] = useState([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const user = useSelector((state) => state.session.user);
  const dispatch = useDispatch();

  const onLogin = async (e) => {
    e.preventDefault();
    const data = await dispatch(login(email, password));
    if (data) {
      setErrors(data);
    }
  };

  const demoLogIn = async (e) => {
    await dispatch(login("demo@aa.io", "password"));
  };

  const updateEmail = (e) => {
    setEmail(e.target.value);
  };

  const updatePassword = (e) => {
    setPassword(e.target.value);
  };

  if (user) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="login-form-and-other-stuff-container ">
      <h1 className="logo-holder">
        <Wordmark size="lg" />
      </h1>
      <p className="pp-tagline">Share photos with friends.</p>
      <form className="form-container" onSubmit={onLogin}>
        <div>
          {errors.map((error, ind) => (
            <div key={ind}>{error}</div>
          ))}
        </div>
        <div className="form-children">
          <input
            className="form-input-text-boxes"
            name="email"
            type="text"
            placeholder="Email"
            value={email}
            onChange={updateEmail}
          />
        </div>
        <div className="form-children">
          <input
            className="form-input-text-boxes"
            name="password"
            type="password"
            placeholder="Password"
            value={password}
            onChange={updatePassword}
          />
        </div>
        <div className="form-children">
          <button className="form-default-submit-button" type="submit">
            Log in
          </button>
        </div>
      </form>
      <div className="or-styling"> or </div>
      <button className="form-default-submit-button demo" onClick={demoLogIn}>
        Demo Login
      </button>
      <p className="pp-demo-note">
        Postpix is a portfolio demo project. It is not affiliated with any
        other social network. Please don't reuse a real password here.
      </p>
    </div>
  );
};

export default LoginForm;

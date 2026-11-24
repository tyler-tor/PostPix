import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Navigate } from "react-router";
import { login } from "../../store/session";

const LoginForm = () => {
  const [errors, setErrors] = useState([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const user = useSelector((state) => state.session.user);
  const dispatch = useDispatch();

  const signIn = async (address, secret) => {
    setBusy(true);
    const result = await dispatch(login(address, secret));
    setBusy(false);
    if (result) setErrors(result);
  };

  const onLogin = (e) => {
    e.preventDefault();
    signIn(email, password);
  };

  if (user) {
    return <Navigate to="/" replace />;
  }

  return (
    <>
      <h2 id="auth-title">Log in</h2>
      <form className="auth-form" onSubmit={onLogin} noValidate>
        {errors.length > 0 && (
          <ul className="form-errors" role="alert">
            {errors.map((error) => (
              <li key={error}>{error}</li>
            ))}
          </ul>
        )}
        <div className="field">
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            className="input"
            name="email"
            type="email"
            autoComplete="username"
            inputMode="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            className="input"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="btn btn-primary btn-block" type="submit" disabled={busy}>
          Log in
        </button>
      </form>

      <div className="auth-divider" role="separator">
        <span>or</span>
      </div>

      <button
        type="button"
        className="btn btn-secondary btn-block"
        onClick={() => signIn("demo@aa.io", "password")}
        disabled={busy}
      >
        Demo Login
      </button>
      <p className="auth-hint">Look around as a ready-made user. No sign-up needed.</p>
    </>
  );
};

export default LoginForm;

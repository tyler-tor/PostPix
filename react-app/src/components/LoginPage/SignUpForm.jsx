import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Navigate, useNavigate } from "react-router";
import { signUp } from "../../store/session";
import ProPicImageUpload from "./ProPicImageUpload";

const FIELDS = [
  { name: "username", label: "Username", type: "text", autoComplete: "username" },
  { name: "email", label: "Email", type: "email", autoComplete: "email" },
  { name: "password", label: "Password", type: "password", autoComplete: "new-password", hint: "At least 8 characters." },
  { name: "repeat", label: "Repeat password", type: "password", autoComplete: "new-password" },
];

const SignUpForm = () => {
  const [errors, setErrors] = useState([]);
  const [values, setValues] = useState({ username: "", firstName: "", lastName: "", email: "", password: "", repeat: "" });
  const [image, setImage] = useState(null);
  const [busy, setBusy] = useState(false);
  const user = useSelector((state) => state.session.user);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const set = (name) => (e) => setValues((prev) => ({ ...prev, [name]: e.target.value }));

  const onSignUp = async (e) => {
    e.preventDefault();
    if (values.password !== values.repeat) {
      setErrors(["The passwords do not match. Try again."]);
      setValues((prev) => ({ ...prev, password: "", repeat: "" }));
      return;
    }
    setBusy(true);
    const result = await dispatch(
      signUp(values.username, values.email, values.password, values.firstName, values.lastName, image)
    );
    setBusy(false);
    if (result) setErrors(result);
    else navigate("/explore");
  };

  if (user) {
    return <Navigate to="/" replace />;
  }

  return (
    <form className="signup" onSubmit={onSignUp} aria-labelledby="signup-title" noValidate>
      <h2 id="signup-title">Create your Postpix account</h2>
      {errors.length > 0 && (
        <ul className="form-errors" role="alert">
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}
      <div className="signup-grid two">
        <div className="field">
          <label htmlFor="signup-first">First name</label>
          <input id="signup-first" className="input" type="text" autoComplete="given-name" value={values.firstName} onChange={set("firstName")} />
        </div>
        <div className="field">
          <label htmlFor="signup-last">Last name</label>
          <input id="signup-last" className="input" type="text" autoComplete="family-name" value={values.lastName} onChange={set("lastName")} />
        </div>
      </div>
      <div className="signup-grid">
        {FIELDS.map((f) => (
          <div className="field" key={f.name}>
            <label htmlFor={`signup-${f.name}`}>{f.label}</label>
            <input
              id={`signup-${f.name}`}
              className="input"
              type={f.type}
              autoComplete={f.autoComplete}
              value={values[f.name]}
              onChange={set(f.name)}
              aria-describedby={f.hint ? `signup-${f.name}-hint` : undefined}
            />
            {f.hint && (
              <span className="field-hint" id={`signup-${f.name}-hint`}>
                {f.hint}
              </span>
            )}
          </div>
        ))}
      </div>
      <ProPicImageUpload setImage={setImage} />
      <p className="demo-note">
        Postpix is a portfolio demo. Use a made-up email and a password you don't use anywhere else.
      </p>
      <button className="btn btn-primary btn-block" type="submit" disabled={busy}>
        Sign up
      </button>
    </form>
  );
};

export default SignUpForm;

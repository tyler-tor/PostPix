import React from "react";
import { Link } from "react-router";
import "./NotFound.css";

// Shown for any URL that no route matches (and for non-numeric profile ids).
const NotFound = () => (
  <main className="not-found">
    <h1>Page not found</h1>
    <p>The page you are looking for does not exist or was moved.</p>
    <Link to="/">Go to the home page</Link>
  </main>
);

export default NotFound;

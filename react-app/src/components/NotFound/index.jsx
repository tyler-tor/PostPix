import React from "react";
import { Link } from "react-router";
import "./NotFound.css";

// Shown for any URL that no route matches, and for profiles that do not exist.
// Pass a title/message to say what exactly was not found.
const NotFound = ({
  title = "Page not found",
  message = "The page you are looking for does not exist or was moved.",
}) => (
  <main className="not-found" id="main">
    <h1>{title}</h1>
    <p>{message}</p>
    <Link to="/" className="btn btn-primary">
      Go to the home page
    </Link>
  </main>
);

export default NotFound;

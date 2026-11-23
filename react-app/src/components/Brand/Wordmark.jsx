import React from "react";
import "./Brand.css";

// Postpix's own text wordmark (no image, no third-party logo or font).
// size: "sm" for the nav bar, "lg" for the login/sign-up cards.
const Wordmark = ({ size = "sm" }) => (
  <span className={`pp-wordmark pp-wordmark-${size}`} aria-label="Postpix">
    <span className="pp-wordmark-mark" aria-hidden="true">P</span>
    <span aria-hidden="true">
      post<span className="pp-wordmark-accent">pix</span>
    </span>
  </span>
);

export default Wordmark;

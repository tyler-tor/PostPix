import React from "react";
import LogoMark from "./LogoMark";
import "./Brand.css";

// Postpix's own logo: the "P" mark plus the lowercase word "postpix" in the
// display font (no image, no third-party logo).
//   size: "sm" (top bar), "lg" (login). tone: "dark" text (default) or "light" (on the teal panel).
const Wordmark = ({ size = "sm", tone = "dark" }) => (
  <span className={`wordmark wordmark-${size} wordmark-${tone}`} role="img" aria-label="Postpix">
    <LogoMark className="wordmark-mark" />
    <span className="wordmark-text" aria-hidden="true">
      post<span className="wordmark-accent">pix</span>
    </span>
  </span>
);

export default Wordmark;

import React from "react";
import LogoMark from "./LogoMark";
import "./Brand.css";

// PostPix's own logo: the "P" mark plus the word "PostPix" (with "Pix" in the accent colour) in the
// display font (no image, no third-party logo).
//   size: "sm" (top bar), "lg" (login). tone: "dark" text (default) or "light" (on the teal panel).
const Wordmark = ({ size = "sm", tone = "dark" }) => (
  <span className={`wordmark wordmark-${size} wordmark-${tone}`} role="img" aria-label="PostPix">
    <LogoMark className="wordmark-mark" />
    <span className="wordmark-text" aria-hidden="true">
      Post<span className="wordmark-accent">Pix</span>
    </span>
  </span>
);

export default Wordmark;

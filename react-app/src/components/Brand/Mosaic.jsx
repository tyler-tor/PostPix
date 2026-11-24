import React from "react";
import "./Mosaic.css";

// A decorative wall of "photos" for the login screen: tinted tiles with simple
// landscape shapes drawn in SVG. Pure CSS/SVG, so it needs no image files and
// never looks like anyone's real pictures. Hidden from screen readers.
const SCENES = {
  sun: (
    <>
      <circle cx="68" cy="34" r="14" fill="currentColor" opacity="0.9" />
      <path d="M0 78 L28 52 L50 70 L72 48 L100 76 V100 H0Z" fill="currentColor" opacity="0.55" />
    </>
  ),
  hills: (
    <>
      <path d="M0 62 Q25 40 50 60 T100 52 V100 H0Z" fill="currentColor" opacity="0.5" />
      <path d="M0 80 Q30 62 60 78 T100 72 V100 H0Z" fill="currentColor" opacity="0.8" />
    </>
  ),
  moon: (
    <>
      <circle cx="40" cy="38" r="16" fill="currentColor" opacity="0.95" />
      <circle cx="48" cy="33" r="14" fill="var(--tile-bg)" />
      <path d="M0 84 L34 66 L58 80 L100 60 V100 H0Z" fill="currentColor" opacity="0.5" />
    </>
  ),
  lines: (
    <>
      <path d="M-10 70 L110 20" stroke="currentColor" strokeWidth="10" opacity="0.5" />
      <path d="M-10 92 L110 42" stroke="currentColor" strokeWidth="10" opacity="0.8" />
    </>
  ),
  dots: (
    <>
      <circle cx="30" cy="30" r="9" fill="currentColor" opacity="0.9" />
      <circle cx="62" cy="52" r="14" fill="currentColor" opacity="0.6" />
      <circle cx="40" cy="78" r="7" fill="currentColor" opacity="0.8" />
    </>
  ),
};

const TILES = [
  { tone: "teal", scene: "sun", tall: true },
  { tone: "sand", scene: "hills" },
  { tone: "deep", scene: "moon" },
  { tone: "mint", scene: "lines" },
  { tone: "teal", scene: "dots" },
  { tone: "sand", scene: "sun", tall: true },
  { tone: "deep", scene: "hills" },
  { tone: "mint", scene: "moon" },
];

const Mosaic = () => (
  <div className="mosaic" aria-hidden="true">
    {TILES.map((tile, i) => (
      <div key={i} className={`mosaic-tile tone-${tile.tone}${tile.tall ? " tall" : ""}`}>
        <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice" focusable="false">
          {SCENES[tile.scene]}
        </svg>
      </div>
    ))}
  </div>
);

export default Mosaic;

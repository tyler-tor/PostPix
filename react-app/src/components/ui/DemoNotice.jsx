import React, { useState } from "react";
import { FiInfo, FiX } from "react-icons/fi";
import "./ui.css";

// Shown while logged in as the shared demo account (session.user.isDemo):
// visitors should know their changes do not last. `flask demo reset` restores
// the demo data every night.
// Dismissing it is remembered for this browser tab session (sessionStorage),
// so it comes back in a new session but does not nag on every page.
export const DEMO_NOTICE_KEY = "postpix.demoNoticeDismissed";

const wasDismissed = () => {
  try {
    return sessionStorage.getItem(DEMO_NOTICE_KEY) === "1";
  } catch {
    return false; // storage blocked (private mode etc.): just show it
  }
};

const DemoNotice = () => {
  const [hidden, setHidden] = useState(wasDismissed);
  if (hidden) return null;

  const dismiss = () => {
    try {
      sessionStorage.setItem(DEMO_NOTICE_KEY, "1");
    } catch {
      /* not remembered, still hidden for now */
    }
    setHidden(true);
    // The button disappears with the banner; keep keyboard focus somewhere useful.
    document.getElementById("main")?.focus({ preventScroll: true });
  };

  return (
    <aside className="demo-notice" aria-label="Demo account notice">
      <div className="demo-notice-inner" role="status">
        <FiInfo className="demo-notice-icon" aria-hidden="true" />
        <p>
          You're using the demo account. Demo data resets nightly, so changes you make here will
          be cleared.
        </p>
        <button type="button" className="icon-btn demo-notice-close" aria-label="Dismiss demo account notice" onClick={dismiss}>
          <FiX aria-hidden="true" />
        </button>
      </div>
    </aside>
  );
};

export default DemoNotice;

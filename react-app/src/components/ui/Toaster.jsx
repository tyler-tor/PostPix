import React, { useEffect, useRef, useSyncExternalStore } from "react";
import { FiX } from "react-icons/fi";
import { subscribe, getToasts, dismissToast } from "../../utils/toast";
import "./ui.css";

// Messages that appear for a few seconds at the bottom of the screen. The
// region is announced politely; errors use role="alert" so they interrupt.
const Toaster = () => {
  const items = useSyncExternalStore(subscribe, getToasts);
  const ref = useRef(null);
  // A popover sits in the browser's top layer, so a message is still visible
  // when a dialog is open (a plain fixed element would be hidden behind it).
  // Re-showing it moves it above a dialog that opened after it.
  useEffect(() => {
    const el = ref.current;
    if (!el || !el.showPopover) return;
    try {
      el.hidePopover();
    } catch {
      /* was not open */
    }
    if (items.length) el.showPopover();
  }, [items]);
  return (
    <div className="toaster" aria-live="polite" popover="manual" ref={ref}>
      {items.map((item) => (
        <div key={item.id} className={`toast toast-${item.kind}`} role={item.kind === "error" ? "alert" : "status"}>
          <p>{item.message}</p>
          <button type="button" className="icon-btn icon-btn-sm" aria-label="Dismiss message" onClick={() => dismissToast(item.id)}>
            <FiX aria-hidden="true" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default Toaster;

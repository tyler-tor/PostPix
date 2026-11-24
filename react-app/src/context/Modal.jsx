import React, { useEffect, useId, useRef } from "react";
import { FiX } from "react-icons/fi";
import "./Modal.css";

// Dialog built on the browser's native <dialog> element (opened with showModal()), which gives:
//   * Escape closes it (the browser fires "cancel" then "close"),
//   * keyboard focus is trapped inside and the page behind becomes inert,
//   * it is announced as a modal dialog by screen readers (role + aria-modal),
//   * it sits in the "top layer", above every other element.
// On top of that this component:
//   * moves focus back to the button that opened it when it closes,
//   * stops the page behind from scrolling,
//   * closes on a click on the dim backdrop,
//   * needs a name for screen readers: pass `title` (shown as a heading) or `label` (not shown).
//
//   <Modal title="New post" onClose={close}> ...form... </Modal>
//   <Modal label="Post by sam" size="lg" bare onClose={close}> ...own layout... </Modal>
//
// size: "sm" | "md" | "lg". On phones sm/md become a sheet from the bottom, lg fills the screen.
// bare: no header; the content draws its own (it should include a close button).

let openDialogs = 0; // so the page unlocks only when the last dialog closes

export function Modal({ onClose, title, label, size = "md", bare = false, children }) {
  const ref = useRef(null);
  const titleId = useId();
  const closing = useRef(false);

  useEffect(() => {
    const dialog = ref.current;
    const opener = document.activeElement;
    closing.current = false; // (React StrictMode runs this effect twice in development)
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", ""); // very old browsers: still visible, just not modal

    openDialogs += 1;
    document.documentElement.classList.add("modal-open");

    return () => {
      openDialogs -= 1;
      if (openDialogs === 0) document.documentElement.classList.remove("modal-open");
      closing.current = true; // unmounting: do not report this close to the parent again
      if (dialog.open && typeof dialog.close === "function") dialog.close();
      // Give focus back to what opened the dialog (if it is still on the page).
      if (opener && opener !== document.body && document.contains(opener) && opener.focus) opener.focus();
    };
  }, []);

  const handleClose = () => {
    // "close" fires after Escape or dialog.close(); tell the parent once.
    // If the dialog is open again, this was a stale event from a previous
    // open (React StrictMode mounts, unmounts and mounts again in development).
    if (!closing.current && !ref.current?.open) {
      closing.current = true;
      onClose();
    }
  };

  const handleBackdrop = (e) => {
    // The dialog box itself has no padding, so a click whose target IS the
    // dialog element landed on the backdrop.
    if (e.target === ref.current) onClose();
  };

  return (
    <dialog
      ref={ref}
      className={`dialog dialog-${size}${bare ? " dialog-bare" : ""}`}
      aria-labelledby={title ? titleId : undefined}
      aria-label={title ? undefined : label}
      onClose={handleClose}
      onClick={handleBackdrop}
    >
      {bare ? (
        children
      ) : (
        <div className="dialog-panel">
          <div className="dialog-head">
            <h2 id={titleId}>{title}</h2>
            <button type="button" className="icon-btn" aria-label="Close" onClick={onClose}>
              <FiX aria-hidden="true" />
            </button>
          </div>
          <div className="dialog-body">{children}</div>
        </div>
      )}
    </dialog>
  );
}

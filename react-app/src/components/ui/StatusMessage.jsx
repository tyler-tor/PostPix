import React from "react";
import "./ui.css";

// Empty and error states: say what happened and what to do next.
//   <StatusMessage title="No posts yet" message="..." action={<Link/>} />
//   kind="error" announces itself to screen readers.
const StatusMessage = ({ title, message, action, kind = "empty" }) => (
  <div className="status-message" role={kind === "error" ? "alert" : undefined}>
    <p className="status-title">{title}</p>
    {message && <p>{message}</p>}
    {action}
  </div>
);

export default StatusMessage;

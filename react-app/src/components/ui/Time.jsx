import React from "react";
import formatDate from "../../utils/formatDate";

// A date as a <time> element: short text ("Nov 23, 2026"), exact moment in the tooltip.
const Time = ({ iso, className }) => {
  if (!iso) return null;
  return (
    <time className={className} dateTime={iso} title={new Date(iso).toLocaleString()}>
      {formatDate(iso)}
    </time>
  );
};

export default Time;

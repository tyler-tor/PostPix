import React from "react";
import "./PostGrid.css";
import SinglePostModal from "./SinglePostModal";

// A grid of post thumbnails. Pass the ids to show, in order; each tile opens
// its post in a modal. No data is fetched here.
const PostGrid = ({ postIds }) => (
  <div className="post-grid-container">
    {postIds.map((id) => (
      <div className="post-grid-children first-two-grid-children" key={id}>
        <SinglePostModal postId={id} />
      </div>
    ))}
  </div>
);

export default PostGrid;

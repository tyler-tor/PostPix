import React from "react";
import PostTile from "./PostTile";
import "./PostGrid.css";

// A responsive grid of photo tiles (ids in the order to show them).
// `mosaic` makes every 7th photo twice as big, which gives the Explore page
// its rhythm; profiles use the plain grid.
const PostGrid = ({ postIds, mosaic = false }) => (
  <ul className={`post-grid${mosaic ? " post-grid-mosaic" : ""}`}>
    {postIds.map((id, index) => {
      const featured = mosaic && index % 7 === 0;
      return (
        <li key={id} className={featured ? "featured" : undefined}>
          <PostTile postId={id} featured={featured} />
        </li>
      );
    })}
  </ul>
);

export default PostGrid;

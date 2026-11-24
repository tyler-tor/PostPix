import React from "react";
import Following from "./Following";
import ActualFeed from "./ActualFeed";
import Rail from "./Rail";
import "./HomeFeed.css";

const HomeFeed = () => (
  <div className="home">
    <div className="home-main">
      <h1 className="visually-hidden">Home</h1>
      <Following />
      <ActualFeed />
    </div>
    <Rail />
  </div>
);

export default HomeFeed;

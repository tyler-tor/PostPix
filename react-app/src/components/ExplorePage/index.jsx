import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import PostGrid from "../reUsedComponents/PostGrid";
import { loadExplore } from "../../store/feeds";
import "./ExplorePage.css";

const ExplorePage = () => {
  const dispatch = useDispatch();
  const ids = useSelector((state) => state.feeds.explore.ids);

  useEffect(() => {
    dispatch(loadExplore());
  }, [dispatch]);

  return (
    <div className="explore-papa-div">
      <div className="explore-page-wrapper">
        <PostGrid postIds={ids} />
      </div>
    </div>
  );
};

export default ExplorePage;

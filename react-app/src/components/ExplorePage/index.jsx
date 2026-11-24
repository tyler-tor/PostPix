import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import PostGrid from "../Post/PostGrid";
import { loadExplore, loadMoreFeed } from "../../store/feeds";
import LoadMore from "../reUsedComponents/LoadMore";
import "./ExplorePage.css";

const ExplorePage = () => {
  const dispatch = useDispatch();
  const { ids, nextCursor, loadingMore } = useSelector((state) => state.feeds.explore);

  useEffect(() => {
    dispatch(loadExplore());
  }, [dispatch]);

  return (
    <div className="page-wide">
      <h1 className="page-title">Explore</h1>
      <PostGrid postIds={ids} mosaic />
      <LoadMore hasMore={!!nextCursor} loading={loadingMore} onLoadMore={() => dispatch(loadMoreFeed("explore"))} label="Load more posts" />
    </div>
  );
};

export default ExplorePage;

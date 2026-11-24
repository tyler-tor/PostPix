import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import PostGrid from "../Post/PostGrid";
import { loadExplore, loadMoreFeed } from "../../store/feeds";
import LoadMore from "../reUsedComponents/LoadMore";
import StatusMessage from "../ui/StatusMessage";
import { GridSkeleton } from "../ui/Skeletons";
import "./ExplorePage.css";

const ExplorePage = () => {
  const dispatch = useDispatch();
  const { ids, nextCursor, loadingMore, status, error } = useSelector((state) => state.feeds.explore);

  useEffect(() => {
    dispatch(loadExplore());
  }, [dispatch]);

  return (
    <div className="page-wide">
      <h1 className="page-title">Explore</h1>
      {ids.length === 0 && status === "error" && (
        <StatusMessage
          kind="error"
          title="Could not load Explore"
          message={error}
          action={<button type="button" className="btn btn-primary" onClick={() => dispatch(loadExplore())}>Try again</button>}
        />
      )}
      {ids.length === 0 && status === "ready" && <StatusMessage title="Nothing here yet" message="Photos shared on PostPix show up here." />}
      {ids.length === 0 && status !== "error" && status !== "ready" && <GridSkeleton />}
      <PostGrid postIds={ids} mosaic />
      <LoadMore hasMore={!!nextCursor} loading={loadingMore} onLoadMore={() => dispatch(loadMoreFeed("explore"))} label="Load more posts" />
    </div>
  );
};

export default ExplorePage;

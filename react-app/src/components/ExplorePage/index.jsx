import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import PostGrid from "../reUsedComponents/PostGrid";
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
    <div className="explore-papa-div">
      <div className="explore-page-wrapper">
        <PostGrid postIds={ids} />
        <LoadMore
          hasMore={!!nextCursor}
          loading={loadingMore}
          onLoadMore={() => dispatch(loadMoreFeed("explore"))}
          label="Load more posts"
        />
      </div>
    </div>
  );
};

export default ExplorePage;

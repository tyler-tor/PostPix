import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { loadHomeFeed, loadMoreFeed } from "../../store/feeds";
import LoadMore from "../reUsedComponents/LoadMore";
import FeedPost from "./FeedPost";

const ActualFeed = () => {
  const dispatch = useDispatch();
  const { ids, nextCursor, loadingMore } = useSelector((state) => state.feeds.home);

  useEffect(() => {
    dispatch(loadHomeFeed());
  }, [dispatch]);

  return (
    <div className="feed-list">
      {ids.map((id, index) => (
        <FeedPost key={id} postId={id} priority={index === 0} />
      ))}
      <LoadMore hasMore={!!nextCursor} loading={loadingMore} onLoadMore={() => dispatch(loadMoreFeed("home"))} label="Load more posts" />
    </div>
  );
};

export default ActualFeed;

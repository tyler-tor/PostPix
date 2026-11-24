import React, { useEffect } from "react";
import { Link } from "react-router";
import { useSelector, useDispatch } from "react-redux";
import { loadHomeFeed, loadMoreFeed } from "../../store/feeds";
import LoadMore from "../reUsedComponents/LoadMore";
import FeedPost from "./FeedPost";
import StatusMessage from "../ui/StatusMessage";
import { FeedSkeleton } from "../ui/Skeletons";

const ActualFeed = () => {
  const dispatch = useDispatch();
  const { ids, nextCursor, loadingMore, status, error } = useSelector((state) => state.feeds.home);

  useEffect(() => {
    dispatch(loadHomeFeed());
  }, [dispatch]);

  if (status === "error" && ids.length === 0) {
    return (
      <StatusMessage
        kind="error"
        title="Could not load your feed"
        message={error}
        action={<button type="button" className="btn btn-primary" onClick={() => dispatch(loadHomeFeed())}>Try again</button>}
      />
    );
  }
  if (ids.length === 0) {
    if (status === "ready") {
      return (
        <StatusMessage
          title="Your feed is empty"
          message="Follow people to see their photos here, or share your own."
          action={<Link to="/explore" className="btn btn-primary">Find people on Explore</Link>}
        />
      );
    }
    return <FeedSkeleton />;
  }

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

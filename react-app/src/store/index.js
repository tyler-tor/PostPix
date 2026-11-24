import { configureStore } from "@reduxjs/toolkit";
// Named import: redux-logger is an old CommonJS package and its default
import { createLogger } from "redux-logger";
import postsReducer from "./post";
import commentsReducer from "./comments";
import session from "./session";
import followingReducer from "./following";
import usersReducer from "./users";
import userLikesReducer from "./user_likes";
import userPostLikeReducer from "./user_post_like_list";
import currentPostReducer from "./currentPost";
import followingPostsReducer from "./followingPosts";
import followersReducer from "./follower";
import nonFollowingReducer from "./nonFollowed";
import searchUserReducer from "./search_users";
import profileFollowingReducer from "./profile_following_store";
import profileUserReducer from "./profileUser";

// One entry per slice. The key is the name components use in useSelector,
const reducer = {
  session,
  posts: postsReducer,
  comments: commentsReducer,
  follow: followingReducer,
  users: usersReducer,
  currentPost: currentPostReducer,
  userLikes: userLikesReducer,
  userPostLikes: userPostLikeReducer,
  followingPosts: followingPostsReducer,
  followers: followersReducer,
  notFollowed: nonFollowingReducer,
  searchUsers: searchUserReducer,
  profileFollowing: profileFollowingReducer,
  profileUser: profileUserReducer,
};

// configureStore (Redux Toolkit) sets up redux-thunk, the Redux DevTools
// browser extension and, in development, checks that catch accidental state
// mutation. redux-logger is added in development only.
const configureAppStore = (preloadedState) =>
  configureStore({
    reducer,
    preloadedState,
    middleware: (getDefaultMiddleware) =>
      import.meta.env.DEV
        ? getDefaultMiddleware().concat(createLogger({ collapsed: true }))
        : getDefaultMiddleware(),
  });

export default configureAppStore;

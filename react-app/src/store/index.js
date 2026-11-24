import { combineReducers, configureStore } from "@reduxjs/toolkit";
// Named import: redux-logger is an old CommonJS package and its default
// export is not reliably a function after bundling.
import { createLogger } from "redux-logger";
import session from "./session";
import users from "./users";
import posts from "./posts";
import feeds from "./feeds";
import profile from "./profile";
import comments from "./comments";

// Six slices; the key is the name components use in useSelector,
// e.g. useSelector((state) => state.posts.byId[id]).
//   session   the logged-in user
//   users     users by id, plus the home page's following / suggestion id lists
//   posts     posts by id (the one place post data lives)
//   feeds     ordered post ids for the home feed and the explore page
//   profile   the open profile page: user id, load status, its post ids
//   comments  comments of the post open in the modal
const appReducer = combineReducers({ session, users, posts, feeds, profile, comments });

// Logging out wipes every slice, so the next person to log in on this browser
// never sees the previous user's likes, feeds or counts.
const reducer = (state, action) =>
  appReducer(action.type === "session/removeUser" ? undefined : state, action);

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

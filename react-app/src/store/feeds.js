import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { upsertPosts, postCreated, postRemoved } from "./posts";

// Ordered lists of post ids for the two post lists that are not tied to a user:
// "home" (people you follow, plus you) and "explore" (everyone).
// status: idle | loading | ready | error
const emptyFeed = () => ({ ids: [], status: "idle", error: null });

const feedsSlice = createSlice({
  name: "feeds",
  initialState: { home: emptyFeed(), explore: emptyFeed() },
  reducers: {
    feedLoading(state, action) {
      state[action.payload].status = "loading";
      state[action.payload].error = null;
    },
    feedLoaded(state, action) {
      const { feed, ids } = action.payload;
      state[feed] = { ids, status: "ready", error: null };
    },
    feedFailed(state, action) {
      const { feed, error } = action.payload;
      state[feed].status = "error";
      state[feed].error = error;
    },
    clearFeeds: () => ({ home: emptyFeed(), explore: emptyFeed() }),
  },
  extraReducers: (builder) => {
    builder
      // A new post goes to the top of both lists (it is newest, and yours).
      .addCase(postCreated, (state, action) => {
        for (const feed of [state.home, state.explore]) {
          if (feed.status === "ready") feed.ids.unshift(action.payload.id);
        }
      })
      .addCase(postRemoved, (state, action) => {
        for (const feed of [state.home, state.explore]) {
          feed.ids = feed.ids.filter((id) => id !== action.payload.id);
        }
      });
  },
});

export const { clearFeeds } = feedsSlice.actions;
const { feedLoading, feedLoaded, feedFailed } = feedsSlice.actions;

const loadFeed = (feed, url) => async (dispatch) => {
  dispatch(feedLoading(feed));
  const res = await api(url);
  if (!res.ok) {
    dispatch(feedFailed({ feed, error: res.errors[0] }));
    return res;
  }
  dispatch(upsertPosts(res.data.Posts));
  dispatch(feedLoaded({ feed, ids: res.data.Posts.map((post) => post.id) }));
  return res;
};

export const loadHomeFeed = () => loadFeed("home", "/api/me/following/posts");
export const loadExplore = () => loadFeed("explore", "/api/posts/");

export default feedsSlice.reducer;

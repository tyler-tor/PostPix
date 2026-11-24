import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { upsertPosts, postCreated, postRemoved } from "./posts";

// Ordered lists of post ids for the two post lists that are not tied to a user:
// "home" (people you follow, plus you) and "explore" (everyone).
// status: idle | loading | ready | error
const emptyFeed = () => ({ ids: [], status: "idle", error: null, nextCursor: null, loadingMore: false });

const URLS = { home: "/api/me/following/posts", explore: "/api/posts/" };

const feedsSlice = createSlice({
  name: "feeds",
  initialState: { home: emptyFeed(), explore: emptyFeed() },
  reducers: {
    feedLoading(state, action) {
      state[action.payload].status = "loading";
      state[action.payload].error = null;
    },
    feedLoaded(state, action) {
      const { feed, ids, nextCursor } = action.payload;
      state[feed] = { ...emptyFeed(), ids, nextCursor, status: "ready" };
    },
    feedMoreLoading(state, action) {
      state[action.payload].loadingMore = true;
    },
    feedMoreLoaded(state, action) {
      const { feed, ids, nextCursor } = action.payload;
      const known = new Set(state[feed].ids);
      state[feed].ids.push(...ids.filter((id) => !known.has(id)));
      state[feed].nextCursor = nextCursor;
      state[feed].loadingMore = false;
    },
    feedMoreFailed(state, action) {
      state[action.payload].loadingMore = false;
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
const { feedLoading, feedLoaded, feedFailed, feedMoreLoading, feedMoreLoaded, feedMoreFailed } =
  feedsSlice.actions;

// First page of a feed (replaces what was there).
const loadFeed = (feed) => async (dispatch) => {
  dispatch(feedLoading(feed));
  const res = await api(URLS[feed]);
  if (!res.ok) {
    dispatch(feedFailed({ feed, error: res.errors[0] }));
    return res;
  }
  dispatch(upsertPosts(res.data.Posts));
  dispatch(feedLoaded({ feed, ids: res.data.Posts.map((post) => post.id), nextCursor: res.data.nextCursor }));
  return res;
};

// The next page, appended below. Does nothing if there is none or one is loading.
export const loadMoreFeed = (feed) => async (dispatch, getState) => {
  const { nextCursor, loadingMore } = getState().feeds[feed];
  if (!nextCursor || loadingMore) return;
  dispatch(feedMoreLoading(feed));
  const res = await api(`${URLS[feed]}?before=${encodeURIComponent(nextCursor)}`);
  if (!res.ok) {
    dispatch(feedMoreFailed(feed));
    return res;
  }
  dispatch(upsertPosts(res.data.Posts));
  dispatch(feedMoreLoaded({ feed, ids: res.data.Posts.map((post) => post.id), nextCursor: res.data.nextCursor }));
  return res;
};

export const loadHomeFeed = () => loadFeed("home");
export const loadExplore = () => loadFeed("explore");

export default feedsSlice.reducer;

import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { upsertPosts, postCreated, postRemoved } from "./posts";
import { upsertUsers } from "./users";

// The profile page that is open: which user, whether it loaded, and that
// user's post ids (newest first).
// status: idle | loading | ready | notFound | error
const profileSlice = createSlice({
  name: "profile",
  initialState: { userId: null, status: "idle", postIds: [], nextCursor: null, loadingMore: false, error: null },
  reducers: {
    profileLoading(state, action) {
      // Keep the old posts only when reloading the same profile.
      if (state.userId !== action.payload) {
        state.postIds = [];
        state.nextCursor = null;
      }
      state.loadingMore = false;
      state.userId = action.payload;
      state.status = "loading";
      state.error = null;
    },
    profileLoaded(state, action) {
      state.status = "ready";
      state.postIds = action.payload.ids;
      state.nextCursor = action.payload.nextCursor;
    },
    moreLoading(state) {
      state.loadingMore = true;
    },
    moreLoaded(state, action) {
      const known = new Set(state.postIds);
      state.postIds.push(...action.payload.ids.filter((id) => !known.has(id)));
      state.nextCursor = action.payload.nextCursor;
      state.loadingMore = false;
    },
    moreFailed(state) {
      state.loadingMore = false;
    },
    profileFailed(state, action) {
      state.status = action.payload.notFound ? "notFound" : "error";
      state.error = action.payload.error;
      state.postIds = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(postCreated, (state, action) => {
        if (state.status === "ready" && state.userId === action.payload.userId) {
          state.postIds.unshift(action.payload.id);
        }
      })
      .addCase(postRemoved, (state, action) => {
        state.postIds = state.postIds.filter((id) => id !== action.payload.id);
      });
  },
});

const { profileLoading, profileLoaded, profileFailed, moreLoading, moreLoaded, moreFailed } = profileSlice.actions;

// The user (counts, follow state) and the first page of their posts.
export const loadProfile = (userId) => async (dispatch) => {
  dispatch(profileLoading(userId));
  const [userRes, postsRes] = await Promise.all([
    api(`/api/users/${userId}`),
    api(`/api/users/${userId}/posts`),
  ]);
  const failed = !userRes.ok ? userRes : !postsRes.ok ? postsRes : null;
  if (failed) {
    dispatch(profileFailed({ notFound: failed.status === 404, error: failed.errors[0] }));
    return failed;
  }
  dispatch(upsertUsers([userRes.data]));
  dispatch(upsertPosts(postsRes.data.Posts));
  dispatch(profileLoaded({ ids: postsRes.data.Posts.map((post) => post.id), nextCursor: postsRes.data.nextCursor }));
  return userRes;
};

export const loadMoreProfilePosts = () => async (dispatch, getState) => {
  const { userId, nextCursor, loadingMore } = getState().profile;
  if (!nextCursor || loadingMore) return;
  dispatch(moreLoading());
  const res = await api(`/api/users/${userId}/posts?before=${encodeURIComponent(nextCursor)}`);
  if (!res.ok) {
    dispatch(moreFailed());
    return res;
  }
  dispatch(upsertPosts(res.data.Posts));
  dispatch(moreLoaded({ ids: res.data.Posts.map((post) => post.id), nextCursor: res.data.nextCursor }));
  return res;
};

export default profileSlice.reducer;

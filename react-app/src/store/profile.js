import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { upsertPosts, postCreated, postRemoved } from "./posts";
import { upsertUsers } from "./users";

// The profile page that is open: which user, whether it loaded, and that
// user's post ids (newest first).
// status: idle | loading | ready | notFound | error
const profileSlice = createSlice({
  name: "profile",
  initialState: { userId: null, status: "idle", postIds: [], error: null },
  reducers: {
    profileLoading(state, action) {
      // Keep the old posts only when reloading the same profile.
      if (state.userId !== action.payload) state.postIds = [];
      state.userId = action.payload;
      state.status = "loading";
      state.error = null;
    },
    profileLoaded(state, action) {
      state.status = "ready";
      state.postIds = action.payload;
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

const { profileLoading, profileLoaded, profileFailed } = profileSlice.actions;

export const loadProfile = (userId) => async (dispatch) => {
  dispatch(profileLoading(userId));
  const res = await api(`/api/users/${userId}`);
  if (!res.ok) {
    dispatch(profileFailed({ notFound: res.status === 404, error: res.errors[0] }));
    return res;
  }
  const { Posts, ...user } = res.data;
  dispatch(upsertUsers([user]));
  dispatch(upsertPosts(Posts));
  dispatch(profileLoaded(Posts.map((post) => post.id)));
  return res;
};

export default profileSlice.reducer;

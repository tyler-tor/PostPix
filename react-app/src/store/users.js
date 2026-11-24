import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { patchUser } from "./session";
import { toast } from "../utils/toast";
import { postCreated, postRemoved } from "./posts";

// Users the app has seen, keyed by id (profile data, follower counts, whether
// you follow them), plus the two small lists the home page needs:
//   followingIds   people the logged-in user follows (the avatar row)
//   suggestionIds  people the logged-in user could follow
const usersSlice = createSlice({
  name: "users",
  initialState: { byId: {}, followingIds: [], suggestionIds: [] },
  reducers: {
    // Merge, so a short summary never wipes the counts we already know.
    upsertUsers(state, action) {
      for (const user of action.payload) {
        state.byId[user.id] = { ...state.byId[user.id], ...user };
      }
    },
    setFollowingIds(state, action) {
      state.followingIds = action.payload;
    },
    setSuggestionIds(state, action) {
      state.suggestionIds = action.payload;
    },
    suggestionRestored(state, action) {
      if (!state.suggestionIds.includes(action.payload)) state.suggestionIds.unshift(action.payload);
    },
    followChanged(state, action) {
      const { id, followed } = action.payload;
      state.followingIds = state.followingIds.filter((x) => x !== id);
      if (followed) state.followingIds.push(id);
      if (followed) state.suggestionIds = state.suggestionIds.filter((x) => x !== id);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(postCreated, (state, action) => {
        const user = state.byId[action.payload.userId];
        if (user) user.postCount += 1;
      })
      .addCase(postRemoved, (state, action) => {
        const user = state.byId[action.payload.userId];
        if (user && user.postCount > 0) user.postCount -= 1;
      });
  },
});

export const { upsertUsers } = usersSlice.actions;
const { setFollowingIds, setSuggestionIds, followChanged, suggestionRestored } = usersSlice.actions;

export const selectUser = (id) => (state) => state.users.byId[id];

export const loadFollowing = () => async (dispatch, getState) => {
  const me = getState().session.user;
  const res = await api(`/api/users/${me.id}/following`);
  if (res.ok) {
    dispatch(upsertUsers(res.data.following));
    dispatch(setFollowingIds(res.data.following.map((user) => user.id)));
  }
  return res;
};

export const loadSuggestions = () => async (dispatch, getState) => {
  const me = getState().session.user;
  const res = await api(`/api/users/${me.id}/notfollowing?limit=8`);
  if (res.ok) {
    dispatch(upsertUsers(res.data.users));
    dispatch(setSuggestionIds(res.data.users.map((user) => user.id)));
  }
  return res;
};

// Follow (follow = true) or unfollow a user. Returns null or an array of errors.
// Optimistic: the button and the follower count change at once; if the request
// fails they go back and a message appears.
export const setFollow = (id, follow) => async (dispatch, getState) => {
  const before = getState().users.byId[id];
  const me = getState().session.user;
  const wasSuggested = getState().users.suggestionIds.includes(id);
  const previous = before && { isFollowedByMe: before.isFollowedByMe, followerCount: before.followerCount };
  if (before) {
    dispatch(upsertUsers([{ id, isFollowedByMe: follow, followerCount: Math.max(0, before.followerCount + (follow ? 1 : -1)) }]));
  }
  dispatch(followChanged({ id, followed: follow }));
  dispatch(patchUser({ followingCount: Math.max(0, me.followingCount + (follow ? 1 : -1)) }));

  const res = await api(`/api/users/${id}/follow`, { method: follow ? "POST" : "DELETE" });
  if (!res.ok) {
    if (previous) dispatch(upsertUsers([{ id, ...previous }]));
    dispatch(followChanged({ id, followed: !follow }));
    if (wasSuggested) dispatch(suggestionRestored(id));
    dispatch(patchUser({ followingCount: me.followingCount }));
    toast(follow ? "Could not follow. Try again." : "Could not unfollow. Try again.", "error");
    return res.errors;
  }
  dispatch(upsertUsers([res.data.followingUser]));
  dispatch(patchUser({ followingCount: res.data.currentUser.followingCount }));
  return null;
};

export default usersSlice.reducer;

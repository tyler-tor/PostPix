import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// Home feed: posts from people the current user follows, keyed by post id.
const followingPostsSlice = createSlice({
  name: "followingPosts",
  initialState: {},
  reducers: {
    // Replace the whole list (so removed items disappear).
    setFollowingPosts: (state, action) => keyBy(action.payload, "id"),
  },
});

const { setFollowingPosts } = followingPostsSlice.actions;

export const getAllFollowingPosts = () => async (dispatch) => {
  const response = await apiFetch("/api/me/following/posts");
  if (response.ok) {
      const data = await response.json();
      dispatch(setFollowingPosts(data.Posts));
      return data;
  }
  return response;
}

export default followingPostsSlice.reducer;

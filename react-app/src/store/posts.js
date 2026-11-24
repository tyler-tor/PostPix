import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { toast } from "../utils/toast";

// Every post the app has seen, keyed by id. Feeds and profiles only keep lists
// of ids; this is the single place a post's data (likes, likedByMe, caption,
// commentCount, author) lives, so a like in the modal shows up everywhere.
const postsSlice = createSlice({
  name: "posts",
  initialState: { byId: {} },
  reducers: {
    upsertPosts(state, action) {
      for (const post of action.payload) state.byId[post.id] = post;
    },
    patchPost(state, action) {
      const { id, ...changes } = action.payload;
      if (state.byId[id]) Object.assign(state.byId[id], changes);
    },
    // Other slices listen to these two (feeds, profile, users).
    postCreated(state, action) {
      state.byId[action.payload.id] = action.payload;
    },
    postRemoved(state, action) {
      delete state.byId[action.payload.id];
    },
  },
});

export const { upsertPosts, patchPost, postCreated, postRemoved } = postsSlice.actions;

export const selectPost = (id) => (state) => state.posts.byId[id];

// Thunks return null on success, or an array of error messages.

export const fetchPost = (id) => async (dispatch) => {
  const res = await api(`/api/posts/${id}`);
  if (res.ok) dispatch(upsertPosts([res.data]));
  return res;
};

export const createPost = ({ caption, imgUrl, thumbUrl, width, height }) => async (dispatch) => {
  const res = await api("/api/posts/", {
    method: "POST",
    json: { caption, img_url: imgUrl, thumb_url: thumbUrl, img_width: width, img_height: height },
  });
  if (!res.ok) return res.errors;
  dispatch(postCreated(res.data));
  toast("Post shared.");
  return null;
};

export const editCaption = (id, caption) => async (dispatch) => {
  const res = await api(`/api/posts/${id}`, { method: "PUT", json: { caption } });
  if (!res.ok) return res.errors;
  dispatch(upsertPosts([res.data]));
  return null;
};

export const deletePost = (id) => async (dispatch, getState) => {
  const post = getState().posts.byId[id];
  const res = await api(`/api/posts/${id}`, { method: "DELETE" });
  if (!res.ok) return res.errors;
  dispatch(postRemoved({ id, userId: post?.userId }));
  toast("Post deleted.");
  return null;
};

// Like or unlike, depending on the current state of the post.
// Optimistic: the heart and the count change at once, the request follows, and
// if it fails the post goes back to how it was and a message appears.
// A second tap while the request is running is ignored (it would double-count).
const liking = new Set();

export const toggleLike = (id) => async (dispatch, getState) => {
  const post = getState().posts.byId[id];
  if (!post) return ["Post not found"];
  if (liking.has(id)) return null;
  liking.add(id);
  const { likes, likedByMe } = post;
  dispatch(patchPost({ id, likedByMe: !likedByMe, likes: Math.max(0, likes + (likedByMe ? -1 : 1)) }));
  const res = await api(`/api/posts/${id}/likes`, { method: likedByMe ? "DELETE" : "POST" });
  liking.delete(id);
  if (!res.ok) {
    dispatch(patchPost({ id, likes, likedByMe }));
    toast(likedByMe ? "Could not remove your like. Try again." : "Could not like this post. Try again.", "error");
    return res.errors;
  }
  dispatch(patchPost({ id, likes: res.data.likes, likedByMe: res.data.likedByMe }));
  return null;
};

export default postsSlice.reducer;

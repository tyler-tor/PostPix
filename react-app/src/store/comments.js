import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { patchPost } from "./posts";

// Comments of the post that is open in the modal (oldest first).
// status: idle | loading | ready | error
const commentsSlice = createSlice({
  name: "comments",
  initialState: { postId: null, byId: {}, ids: [], status: "idle" },
  reducers: {
    commentsLoading(state, action) {
      if (state.postId !== action.payload) {
        state.byId = {};
        state.ids = [];
      }
      state.postId = action.payload;
      state.status = "loading";
    },
    commentsLoaded(state, action) {
      state.status = "ready";
      state.byId = Object.fromEntries(action.payload.map((c) => [c.id, c]));
      state.ids = action.payload.map((c) => c.id);
    },
    commentsFailed(state) {
      state.status = "error";
    },
    commentAdded(state, action) {
      state.byId[action.payload.id] = action.payload;
      state.ids.push(action.payload.id);
    },
    commentChanged(state, action) {
      state.byId[action.payload.id] = action.payload;
    },
    commentRemoved(state, action) {
      delete state.byId[action.payload];
      state.ids = state.ids.filter((id) => id !== action.payload);
    },
  },
});

const { commentsLoading, commentsLoaded, commentsFailed, commentAdded, commentChanged, commentRemoved } =
  commentsSlice.actions;

export const loadComments = (postId) => async (dispatch) => {
  dispatch(commentsLoading(postId));
  const res = await api(`/api/posts/${postId}/comments`);
  if (res.ok) dispatch(commentsLoaded(res.data.Comments));
  else dispatch(commentsFailed());
  return res;
};

// The thunks below return null on success, or an array of error messages.

export const addComment = (postId, body) => async (dispatch, getState) => {
  const res = await api(`/api/posts/${postId}/comments`, { method: "POST", json: { body } });
  if (!res.ok) return res.errors;
  dispatch(commentAdded(res.data));
  const post = getState().posts.byId[postId];
  if (post) dispatch(patchPost({ id: postId, commentCount: post.commentCount + 1 }));
  return null;
};

export const editComment = (id, body) => async (dispatch) => {
  const res = await api(`/api/comments/${id}`, { method: "PUT", json: { body } });
  if (!res.ok) return res.errors;
  dispatch(commentChanged(res.data));
  return null;
};

export const deleteComment = (id) => async (dispatch, getState) => {
  const comment = getState().comments.byId[id];
  const res = await api(`/api/comments/${id}`, { method: "DELETE" });
  if (!res.ok) return res.errors;
  dispatch(commentRemoved(id));
  const post = comment && getState().posts.byId[comment.postId];
  if (post) dispatch(patchPost({ id: post.id, commentCount: Math.max(0, post.commentCount - 1) }));
  return null;
};

export default commentsSlice.reducer;

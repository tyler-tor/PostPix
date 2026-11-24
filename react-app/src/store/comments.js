import { createSlice } from "@reduxjs/toolkit";
import { api } from "../utils/api";
import { patchPost } from "./posts";

// Comments of the post that is open in the modal (oldest first).
// status: idle | loading | ready | error
const commentsSlice = createSlice({
  name: "comments",
  initialState: { postId: null, byId: {}, ids: [], status: "idle", nextCursor: null, loadingMore: false },
  reducers: {
    commentsLoading(state, action) {
      if (state.postId !== action.payload) {
        state.byId = {};
        state.ids = [];
        state.nextCursor = null;
      }
      state.loadingMore = false;
      state.postId = action.payload;
      state.status = "loading";
    },
    commentsLoaded(state, action) {
      state.status = "ready";
      state.byId = Object.fromEntries(action.payload.items.map((c) => [c.id, c]));
      state.ids = action.payload.items.map((c) => c.id);
      state.nextCursor = action.payload.nextCursor;
    },
    moreCommentsLoading(state) {
      state.loadingMore = true;
    },
    moreCommentsLoaded(state, action) {
      for (const c of action.payload.items) {
        if (!state.byId[c.id]) state.ids.push(c.id);
        state.byId[c.id] = c;
      }
      state.nextCursor = action.payload.nextCursor;
      state.loadingMore = false;
    },
    moreCommentsFailed(state) {
      state.loadingMore = false;
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

const {
  commentsLoading, commentsLoaded, commentsFailed, commentAdded, commentChanged, commentRemoved,
  moreCommentsLoading, moreCommentsLoaded, moreCommentsFailed,
} = commentsSlice.actions;

export const loadComments = (postId) => async (dispatch) => {
  dispatch(commentsLoading(postId));
  const res = await api(`/api/posts/${postId}/comments`);
  if (res.ok) dispatch(commentsLoaded({ items: res.data.Comments, nextCursor: res.data.nextCursor }));
  else dispatch(commentsFailed());
  return res;
};

export const loadMoreComments = () => async (dispatch, getState) => {
  const { postId, nextCursor, loadingMore } = getState().comments;
  if (!nextCursor || loadingMore) return;
  dispatch(moreCommentsLoading());
  const res = await api(`/api/posts/${postId}/comments?after=${encodeURIComponent(nextCursor)}`);
  if (res.ok) dispatch(moreCommentsLoaded({ items: res.data.Comments, nextCursor: res.data.nextCursor }));
  else dispatch(moreCommentsFailed());
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

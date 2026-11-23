import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// Comments of the post open in the modal, keyed by comment id.
// (Immer lets the reducers "mutate" state safely; RTK makes the copies.)
const commentsSlice = createSlice({
  name: "comments",
  initialState: {},
  reducers: {
    setComments: (state, action) => keyBy(action.payload),
    addComment(state, action) {
      state[action.payload.id] = action.payload;
    },
    updateCommentBody(state, action) {
      const comment = state[action.payload.id];
      if (comment) comment.body = action.payload.body;
    },
    removeComment(state, action) {
      delete state[action.payload];
    },
    clearComments: () => ({}),
  },
});

const { setComments, addComment, updateCommentBody, removeComment } =
  commentsSlice.actions;
export const clearCommentsAction = commentsSlice.actions.clearComments;

export const postComment = (comment) => async (dispatch) => {
  const { postId, body } = comment;
  const response = await apiFetch(`/api/posts/${postId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      body: body,
    }),
  });
  if (response.ok) {
    const newComment = await response.json();
    // console.log('IN THUNK FOR COMMENTS===================', newComment);
    dispatch(addComment(newComment));
    return null;
  }
  else if (response.status < 500) {
    const data = await response.json();
    if (data.errors) {
      // console.log(data.errors);
      return data.errors;
    }
  }
  else{
    return [{'errors': 'an error occured' }]
  }
};

/////// Newly Added///

export const updateComment = (payload) => async (dispatch) => {
  const { commentId, body } = payload;
  const response = await apiFetch(`/api/comments/${commentId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      body: body,
    }),
  });

  if (response.ok) {
    let updatedComment = await response.json()
    // console.log('update comment thunk ------------------------', updatedComment);
    dispatch(
      updateCommentBody({
        body,
        id: commentId,
      })
    );
    return null;
  }
  else if (response.status < 500) {
    const data = await response.json();
    if (data.errors) {
      // console.log(data.errors);
      return data.errors;
    }
  }
  else{
    return [{'errors': 'an error occured' }]
  }

};

export const deleteComment = (commentId) => async (dispatch) => {
  const response = await apiFetch(`/api/comments/${commentId}`, {
    method: "DELETE",
  });
  // console.log(response);
  if (response.ok) {
    const data = await response.json();
    dispatch(removeComment(commentId));
    return data;
  }
};

/////// Newly Added///

export const getAllComments = (id) => async (dispatch) => {
  const response = await apiFetch(`/api/posts/${id}/comments`);

  if (response.ok) {
    const data = await response.json();
    // console.log('IN THUNK---------------------', data);
    dispatch(setComments(data.Comments));
    return data;
  }

  return response;
};

export default commentsSlice.reducer;

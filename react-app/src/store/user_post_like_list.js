//* For getting a user liked post's ids

import { getCurrentPost } from "./currentPost"
import apiFetch from "../utils/apiFetch";

import { createSlice } from "@reduxjs/toolkit";
import { keyBy } from "./helpers";

// Posts the current user has liked: { [postId]: { postId, likes } }.
const userPostLikesSlice = createSlice({
  name: "userPostLikes",
  initialState: {},
  reducers: {
    setLikedPosts: (state, action) => keyBy(action.payload, "postId"),
    addLikedPost(state, action) {
      state[action.payload.postId] = action.payload;
    },
    removeLikedPost(state, action) {
      delete state[action.payload];
    },
  },
});

const { setLikedPosts, addLikedPost, removeLikedPost } = userPostLikesSlice.actions;

export const deleteUserLikedPostId = (postId) => async (dispatch) =>{
    const response = await apiFetch(`/api/posts/${postId}/likes`,{
        method: 'DELETE'
    })
    if(response.ok){
        const data = await response.json();
        //!added a dispatch to current post to update with this thunk
        dispatch(getCurrentPost(data.postId))
        dispatch(removeLikedPost(data.postId))

        return data;
    }
}

export const getUserLikedPostId = () => async (dispatch) =>{
    const response = await apiFetch('/api/users/likes')
    if(response.ok){
        const data = await response.json()
        //!added a dispatch to current post to update with this thunk
        dispatch(setLikedPosts(data.likes))
        return data.likes
    }

}

export const addUserLikedPostId = (postId) => async (dispatch) =>{
    const response = await apiFetch(`/api/posts/${postId}/likes`,{
        method: 'POST',
        headers: {'Content-Type' : 'application/json'},
    })
    if(response.ok){
        const data = await response.json()
        dispatch(getCurrentPost(data.postId))
        dispatch(addLikedPost(data))
    }
}

export default userPostLikesSlice.reducer;

import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";

// The post open in the post modal (with its author in .users).
const currentPostSlice = createSlice({
  name: "currentPost",
  initialState: {},
  reducers: {
    setCurrentPost: (state, action) => ({ ...action.payload }),
  },
});

const { setCurrentPost } = currentPostSlice.actions;

export const getCurrentPost = (postId) => async dispatch=>{
    const response = await apiFetch(`/api/posts/${postId}`)
    if(response.ok){
        const data = await response.json();
        dispatch(setCurrentPost(data))
        return data
    }
}

export default currentPostSlice.reducer;

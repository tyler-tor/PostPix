import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// Users who liked the post open in the modal, keyed by id.
const userLikesSlice = createSlice({
  name: "userLikes",
  initialState: {},
  reducers: {
    // Replace the whole list (so removed items disappear).
    setLikeUsers: (state, action) => keyBy(action.payload, "id"),
  },
});

const { setLikeUsers } = userLikesSlice.actions;

export const getLikesUser = (postId) => async dispatch =>{
    const response = await apiFetch(`/api/posts/${postId}/likes/users`)
    if(response.ok){
        const data = await response.json()
        dispatch(setLikeUsers(data.user))
        return data
    }

}

export default userLikesSlice.reducer;

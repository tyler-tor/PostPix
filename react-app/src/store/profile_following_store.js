import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// Who the profile user follows, keyed by userId.
const profileFollowingSlice = createSlice({
  name: "profileFollowing",
  initialState: {},
  reducers: {
    // Replace the whole list (so removed items disappear).
    setProfileFollowing: (state, action) => keyBy(action.payload, "id"),
  },
});

const { setProfileFollowing } = profileFollowingSlice.actions;

export const getProfileFollowing = (id) => async (dispatch) => {
    const response = await apiFetch(`/api/users/${id}/following`)

    if(response.ok){
        const data = await response.json();
        dispatch(setProfileFollowing(data.following));
        return data
    }
    return response
}



export default profileFollowingSlice.reducer;

import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// Followers of the user whose page is open, keyed by userId.
const followersSlice = createSlice({
  name: "followers",
  initialState: {},
  reducers: {
    // Replace the whole list (so removed items disappear).
    setFollowers: (state, action) => keyBy(action.payload, "userId"),
  },
});

const { setFollowers } = followersSlice.actions;

export const getAllFollowers = (id) => async (dispatch) => {
    const response = await apiFetch(`/api/users/${id}/followers`)

    if(response.ok){
        const data = await response.json();
        dispatch(setFollowers(data.followers));
        return data.followers
    }
    return response
}


export default followersSlice.reducer;

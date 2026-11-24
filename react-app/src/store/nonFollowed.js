import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// Users the current user does not follow yet (home page suggestions), keyed by id.
const notFollowedSlice = createSlice({
  name: "notFollowed",
  initialState: {},
  reducers: {
    // Replace the whole list (so removed items disappear).
    setNonFollowing: (state, action) => keyBy(action.payload, "id"),
  },
});

const { setNonFollowing } = notFollowedSlice.actions;

export const getNonFollowing = (id) => async(dispatch) => {
    const response = await apiFetch(`/api/users/${id}/notfollowing`)
    if(response.ok){
        const data = await response.json();
        dispatch(setNonFollowing(data.users));
        return data
    }
    return response
}

export default notFollowedSlice.reducer;

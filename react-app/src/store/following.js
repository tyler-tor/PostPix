import { createSlice } from "@reduxjs/toolkit";
import { getAllFollowers } from "./follower";
import { getProfileUser } from "./profileUser";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// Users followed by the user passed to getAllFollowing(id), keyed by userId.
const followSlice = createSlice({
  name: "follow",
  initialState: {},
  reducers: {
    // Replace the whole list so unfollowed users disappear.
    setFollowing: (state, action) => keyBy(action.payload, "userId"),
    addFollowingUser(state, action) {
      state[action.payload.id] = action.payload;
    },
    removeFollowingUser(state, action) {
      delete state[action.payload];
    },
  },
});

const { setFollowing, addFollowingUser, removeFollowingUser } = followSlice.actions;

export const deleteFollowing = (id) => async(dispatch) => {
    const response = await apiFetch(`/api/users/${id}/follow`, {
        method: 'DELETE'
    })

    if (response.ok) {
        const data = await response.json()
        dispatch(removeFollowingUser(data.followingUser.id));
        dispatch(getAllFollowing(id))
        dispatch(getAllFollowers(id))
        dispatch(getProfileUser(id))
        return data
    }
}

export const addFollowing = (id) => async(dispatch) => {
    const response = await apiFetch(`/api/users/${id}/follow`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })

    if(response.ok) {
        const data = await response.json()
        dispatch(addFollowingUser(data.followingUser))
        dispatch(getAllFollowing(id))
        dispatch(getAllFollowers(id))
        dispatch(getProfileUser(id))
        return data
    }
}

export const getAllFollowing = (id) => async (dispatch) => {
    const response = await apiFetch(`/api/users/${id}/following`)

    if(response.ok){
        const data = await response.json();
        dispatch(setFollowing(data.following));
        return data
    }
    return response
}

// export const getAllFollowers = (id) => async (dispatch) => {
//     const response = await apiFetch(`/api/users/${id}/followers`)

//     if(response.ok){
//         const data = await response.json();
//         dispatch(getFollowers(data.followers));
//         return data
//     }
//     return response
// }

export default followSlice.reducer;

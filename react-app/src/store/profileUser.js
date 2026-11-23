import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";

// The user whose profile page is open.
const profileUserSlice = createSlice({
  name: "profileUser",
  initialState: {},
  reducers: {
    setProfileUser: (state, action) => ({ ...action.payload }),
  },
});

const { setProfileUser } = profileUserSlice.actions;

export const getProfileUser = (id) => async dispatch =>{
    const response = await apiFetch(`/api/users/${id}`)
    if(response.ok){
        const data = await response.json();
        // console.log('data', data)
        dispatch(setProfileUser(data))
        return data
    }
}


export default profileUserSlice.reducer;

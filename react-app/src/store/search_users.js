import { createSlice } from "@reduxjs/toolkit";
import { keyBy } from "./helpers";

// Users matching the nav bar search box, keyed by id.
const searchUsersSlice = createSlice({
  name: "searchUsers",
  initialState: {},
  reducers: {
    setUsers: (state, action) => keyBy(action.payload, "id"),
  },
});

const { setUsers } = searchUsersSlice.actions;

export const setSearchUsers = (users) => (dispatch) =>{
    if(users){
        dispatch(setUsers(users))
    }
}

export default searchUsersSlice.reducer;

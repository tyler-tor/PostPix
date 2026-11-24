import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";
import { keyBy } from "./helpers";

// All users, keyed by id.
const usersSlice = createSlice({
  name: "users",
  initialState: {},
  reducers: {
    // Replace the whole list (so removed items disappear).
    setUsers: (state, action) => keyBy(action.payload, "id"),
  },
});

const { setUsers } = usersSlice.actions;

export const getAllUsers = () => async (dispatch) => {
    const response = await apiFetch('/api/users/')

    if (response.ok) {
        const data = await response.json();
        dispatch(setUsers(data.users))
        return data
    }
    return response
}
//!moved to its own store.

export default usersSlice.reducer;

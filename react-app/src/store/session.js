import { createSlice } from "@reduxjs/toolkit";
import apiFetch from "../utils/apiFetch";

// The logged-in user (or null).
const sessionSlice = createSlice({
  name: "session",
  initialState: { user: null },
  reducers: {
    setUser(state, action) {
      state.user = action.payload;
    },
    removeUser(state) {
      state.user = null;
    },
  },
});

const { setUser, removeUser } = sessionSlice.actions;

export const authenticate = () => async (dispatch) => {
  const response = await apiFetch("/api/auth/", {
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (response.ok) {
    const data = await response.json();
    if (data.errors) {
      return;
    }

    dispatch(setUser(data));
  }
};

export const login = (email, password) => async (dispatch) => {
  const response = await apiFetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  if (response.ok) {
    const data = await response.json();
    dispatch(setUser(data));
    return null;
  } else if (response.status < 500) {
    const data = await response.json();
    if (data.errors) {
      return data.errors;
    }
  } else {
    return ["An error occurred. Please try again."];
  }
};

export const logout = () => async (dispatch) => {
  const response = await apiFetch("/api/auth/logout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.ok) {
    dispatch(removeUser());
  }
};

export const signUp = (username, email, password, first_name, last_name, image) => async (dispatch) => {
  // Sent as multipart form data so the optional profile picture file can be
  // uploaded in the same request (the upload endpoint requires a logged-in user).
  const formData = new FormData();
  formData.append('username', username);
  formData.append('email', email);
  formData.append('password', password);
  formData.append('first_name', first_name);
  formData.append('last_name', last_name);
  if (image) formData.append('image', image);

  const response = await apiFetch('/api/auth/signup', {
    method: 'POST',
    body: formData,
  });

  if (response.ok) {
    const data = await response.json();
    dispatch(setUser(data));
    return null;
  } else if (response.status < 500) {
    const data = await response.json();
    if (data.errors) {
      return data.errors;
    }
  } else {
    return ["An error occurred. Please try again."];
  }
};

export default sessionSlice.reducer;

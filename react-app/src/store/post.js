import { getCurrentPost } from "./currentPost";
import { clearCommentsAction } from "./comments";
import { getAllFollowing } from "./following";
import { getAllFollowers } from "./follower";
import { getProfileFollowing } from "./profile_following_store";
import { getProfileUser } from "./profileUser";
import apiFetch from "../utils/apiFetch";
import { createSlice } from "@reduxjs/toolkit";
import { keyBy } from "./helpers";

// All posts (explore page and profile grids), keyed by post id.
const postsSlice = createSlice({
  name: "posts",
  initialState: {},
  reducers: {
    // Merge (not replace), like the old reducer did.
    setPosts(state, action) {
      Object.assign(state, keyBy(action.payload));
    },
    // Add and update both store the post the API returned.
    upsertPost(state, action) {
      state[action.payload.id] = action.payload;
    },
    removePost(state, action) {
      delete state[action.payload];
    },
  },
});

const { setPosts, upsertPost, removePost } = postsSlice.actions;

export const deletePost = (id) => async (dispatch) =>{
  const response = await apiFetch(`/api/posts/${id}`,{
    method:'DELETE'
  })
  if(response.ok){
    dispatch(removePost(id))
    // dispatch(clearCommentsAction())

    return 'Sucess!'
  }
  return response;
}

export const updatePost = (caption) => async (dispatch) =>{
  const response = await apiFetch(`/api/posts/${caption.id}`, {
    method: 'PUT',
    headers: {'Content-Type' : 'application/json'},
    body: JSON.stringify({
      caption: caption.caption
    })
  })
  if(response.ok){
    const editedPost = await response.json()
    dispatch(upsertPost(editedPost))
    dispatch(getCurrentPost(caption.id))
    // console.log('DEBUG EDITED POST-------------------', editedPost);
    return null
  }
  else if (response.status < 500) {
    const data = await response.json();
    if (data.errors) {
      // console.log(data.errors);
      return data.errors;
    }
  }
  else{
    return [{'errors': 'an error occured' }]
  }
}

export const addPost = (post) => async (dispatch) =>{
  // console.log('IN THUNK ACTION FOR POST', post);
  const response = await apiFetch('/api/posts/',{
    method: 'POST',
    headers: {'Content-Type' : 'application/json'},
    body: JSON.stringify({
      user_id: post.userId,
      caption: post.caption,
      img_url: post.imgUrl
    })

  })
  if(response.ok){
    const newPost = await response.json()
    dispatch(upsertPost(newPost))
    dispatch(getAllFollowing(post.userId))
    //!added this to update follower numbers
    dispatch(getAllFollowers(post.userId))
    dispatch(getProfileFollowing(post.userId))
    dispatch(getProfileUser(post.userId))
    return null
  }
  else if (response.status < 500) {
    const data = await response.json();
    if (data.errors) {
      // console.log(data.errors);
      return data.errors;
    }
  }
  else{
    return [{'errors': 'an error occured' }]
  }

}

// export const getAllFollowingPosts = () => async (dispatch) => {
//   const response = await apiFetch("/api/me/following/posts");

//   if (response.ok) {
//       const data = await response.json();
//       dispatch(getFollowingPosts(data.Posts));
//       return data;
//   }
//   return response;
// }

export const getAllPosts = () => async (dispatch) => {
  const response = await apiFetch("/api/posts/");

  if (response.ok) {
    const data = await response.json();
    // console.log("test", data);
    dispatch(setPosts(data.Posts));
    return data;
  }

  return response;
};

export default postsSlice.reducer;

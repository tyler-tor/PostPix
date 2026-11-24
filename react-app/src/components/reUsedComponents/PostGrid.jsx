import React, { useEffect } from "react";
import "./PostGrid.css";
import SinglePostModal from "./SinglePostModal";
import stock from "../../images/stock.jpg";
import { useSelector, useDispatch } from "react-redux";
import { useParams } from "react-router";
import { getAllPosts } from "../../store/post";

const PostGrid = () => {
  const { userId } = useParams()
  const user = useSelector((state) => state.users[userId])
  const posts = Object.values(useSelector((state) => state.posts)).reverse()
  const userPosts = posts.filter(post => {
    if(user){
      return post.userId === user.id
    }
  });
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(getAllPosts())
  }, [dispatch])

  return (
    <div className="post-grid-container">
      {user ? (
      userPosts.reverse().map(post => {
        return(
          <div className="post-grid-children first-two-grid-children" key={post.id}>
            <SinglePostModal post={post} />
          </div>
        )
      })) : (
        posts.map(post => {
          return(
            <div className="post-grid-children first-two-grid-children" key={post.id}>
              <SinglePostModal post={post} />
            </div>
          )
        })
      )
      }
    </div>
  );
};

export default PostGrid;

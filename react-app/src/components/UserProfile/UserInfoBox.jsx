import React, { useEffect, useState } from "react";
import PostGrid from "../reUsedComponents/PostGrid";
import { useSelector, useDispatch } from "react-redux";
import { useParams } from "react-router";
import { getAllUsers } from "../../store/users";
import UserFollowerListModal from "../reUsedComponents/UserFollowerListModal";
import {
  addFollowing,
  deleteFollowing,
  getAllFollowing,
} from "../../store/following";
import { getAllFollowers } from "../../store/follower";
import { getProfileFollowing } from "../../store/profile_following_store";
import { getProfileUser } from "../../store/profileUser";
import UserFollowingListModal from "../reUsedComponents/UserFollowingListModal";
import './UserProfile.css'

const UserInfoBox = () => {
  const dispatch = useDispatch();
  const { userId } = useParams();
  const currUser = useSelector((state) => state.session.user);

  const posts = Object.values(useSelector((state) => state.posts));
  const [isLoading, setIsLoading] = useState(false);
  const [followBtn, setFollowBtn] = useState(false);
  const [followTest, setFollowTest] = useState(false);
  const [postCount, setPostCount] = useState(0);
  const profileUser = useSelector(state => state.profileUser)

  useEffect(() =>{

    dispatch(getProfileUser(Number(userId))).then(() =>{
      setIsLoading(true)
    })
  },[dispatch, userId])

  useEffect(() => {
    // The profile payload says whether the logged-in user follows this person.
    setFollowTest(profileUser.id === Number(userId) && !!profileUser.isFollowedByMe);
  }, [userId, profileUser]);

  //   //!might need to run dispatch to get all followers instead of following!

  // //!code here causes a crash if you click the follow button multiple times.
  // //     setFollows('UnFollow')
  // //     setFollows('Follow')
  // //   }
  // // }
  // // }
  const handleFollow = () => {
    dispatch(addFollowing(Number(userId)));
    setFollowTest(true);
  };

  const handleUnFollow = () => {
    dispatch(deleteFollowing(userId));
    setFollowTest(false);
  };

  const userPosts = () => {
    setPostCount(posts.filter((post) => post.userId == profileUser.id).length);
  };

  useEffect(() => {
    userPosts();
  }, [posts]);

  // //     }
  // //   }

  useEffect(() => {
    if (currUser.id !== Number(userId)){
      setFollowBtn(true);

    }
    else{
      setFollowBtn(false)
    }
  });

  return (
    isLoading && (
      <>
        <div className="user-profile-header-container">
          <div className="user-info-box-profile-photo-container">
            <div id="user-profile-wrapper">
              <img src={profileUser.profilePicture} alt="profile" />
            </div>
            <div className="user-profile-details-container">
              <div className="username-and-follow-button-row">
                <div className="username-for-user-profile">{profileUser.username}</div>
                {followBtn && (
                  <>
                    {followTest ? (
                      <button onClick={handleUnFollow} className="unfollow-button">Following</button>
                    ) : (
                      <button onClick={handleFollow} className="follow-button">Follow</button>
                    )}
                  </>
                )}
              </div>
              <div className="posts-followers-following-row">
                <div className="">
                  {" "}
                  <strong>{postCount}</strong> Posts
                </div>
                <div className="posts-followers-following-row-children-except-first">
                  {" "}
                  <UserFollowerListModal userId={userId} />
                </div>
                <div className="posts-followers-following-row-children-except-first slight-margin">
                  <strong>
                    <UserFollowingListModal userId={userId}/>
                  </strong>

                </div>
              </div>
              <div className="user-profile-caption">

              </div>
            </div>
          </div>
        </div>
        <PostGrid />
      </>
    )
  );
};

export default UserInfoBox;

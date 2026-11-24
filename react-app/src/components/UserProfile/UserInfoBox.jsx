import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import PostGrid from "../reUsedComponents/PostGrid";
import UserListModal from "../reUsedComponents/UserListModal";
import { loadProfile } from "../../store/profile";
import { setFollow } from "../../store/users";
import "./UserProfile.css";

const UserInfoBox = ({ userId }) => {
  const dispatch = useDispatch();
  const currUser = useSelector((state) => state.session.user);
  const profile = useSelector((state) => state.profile);
  const profileUser = useSelector((state) => state.users.byId[userId]);
  const [followErrors, setFollowErrors] = useState([]);

  useEffect(() => {
    dispatch(loadProfile(userId));
  }, [dispatch, userId]);

  // Not loaded yet (or this profile failed): nothing to show. P31/Z3 add the
  // loading, error and not-found states.
  if (profile.userId !== userId || profile.status !== "ready" || !profileUser) return null;

  const isMe = currUser.id === userId;

  const handleFollow = async (follow) => {
    setFollowErrors((await dispatch(setFollow(userId, follow))) || []);
  };

  return (
    <>
      <div className="user-profile-header-container">
        <div className="user-info-box-profile-photo-container">
          <div id="user-profile-wrapper">
            <img src={profileUser.profilePicture} alt="profile" />
          </div>
          <div className="user-profile-details-container">
            <div className="username-and-follow-button-row">
              <div className="username-for-user-profile">{profileUser.username}</div>
              {!isMe &&
                (profileUser.isFollowedByMe ? (
                  <button onClick={() => handleFollow(false)} className="unfollow-button">
                    Following
                  </button>
                ) : (
                  <button onClick={() => handleFollow(true)} className="follow-button">
                    Follow
                  </button>
                ))}
            </div>
            {followErrors.map((error) => (
              <div key={error}>{error}</div>
            ))}
            <div className="posts-followers-following-row">
              <div>
                <strong>{profileUser.postCount}</strong> Posts
              </div>
              <div className="posts-followers-following-row-children-except-first">
                <UserListModal url={`/api/users/${userId}/followers`} dataKey="followers">
                  <strong>{profileUser.followerCount}</strong> followers
                </UserListModal>
              </div>
              <div className="posts-followers-following-row-children-except-first slight-margin">
                <UserListModal url={`/api/users/${userId}/following`} dataKey="following">
                  <strong>{profileUser.followingCount}</strong>{" "}
                  <span className="following-text-list">following</span>
                </UserListModal>
              </div>
            </div>
          </div>
        </div>
      </div>
      <PostGrid postIds={profile.postIds} />
    </>
  );
};

export default UserInfoBox;

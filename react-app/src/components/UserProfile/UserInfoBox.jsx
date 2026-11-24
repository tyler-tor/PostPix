import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import PostGrid from "../Post/PostGrid";
import UserListModal from "../reUsedComponents/UserListModal";
import { loadProfile, loadMoreProfilePosts } from "../../store/profile";
import LoadMore from "../reUsedComponents/LoadMore";
import { setFollow } from "../../store/users";
import NotFound from "../NotFound";
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

  // A user id that does not exist gets a proper not-found page instead of an
  // empty shell. (Loading and error states come with P31.)
  if (profile.userId === userId && profile.status === "notFound") {
    return <NotFound title="Profile not found" message="There is no Postpix user with that id. They may have deleted their account." />;
  }
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
      <LoadMore
        hasMore={!!profile.nextCursor}
        loading={profile.loadingMore}
        onLoadMore={() => dispatch(loadMoreProfilePosts())}
        label="Load more posts"
      />
    </>
  );
};

export default UserInfoBox;

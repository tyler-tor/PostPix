import React, { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import PostGrid from "../Post/PostGrid";
import UserListModal from "../reUsedComponents/UserListModal";
import { loadProfile, loadMoreProfilePosts } from "../../store/profile";
import LoadMore from "../reUsedComponents/LoadMore";
import { setFollow } from "../../store/users";
import NotFound from "../NotFound";
import Avatar from "../ui/Avatar";
import StatusMessage from "../ui/StatusMessage";
import { ProfileSkeleton } from "../ui/Skeletons";
import "./UserProfile.css";

const UserInfoBox = ({ userId }) => {
  const dispatch = useDispatch();
  const currUser = useSelector((state) => state.session.user);
  const profile = useSelector((state) => state.profile);
  const profileUser = useSelector((state) => state.users.byId[userId]);

  useEffect(() => {
    dispatch(loadProfile(userId));
  }, [dispatch, userId]);

  // A user id that does not exist gets a proper not-found page instead of an
  // empty shell. (Loading and error states come with P31.)
  if (profile.userId === userId && profile.status === "notFound") {
    return <NotFound title="Profile not found" message="There is no Postpix user with that id. They may have deleted their account." />;
  }
  if (profile.userId === userId && profile.status === "error") {
    return (
      <StatusMessage
        kind="error"
        title="Could not load this profile"
        message={profile.error}
        action={<button type="button" className="btn btn-primary" onClick={() => dispatch(loadProfile(userId))}>Try again</button>}
      />
    );
  }
  if (profile.userId !== userId || profile.status !== "ready" || !profileUser) return <ProfileSkeleton />;

  const isMe = currUser.id === userId;

  const handleFollow = async (follow) => {
    await dispatch(setFollow(userId, follow)); // a failure shows a toast and undoes itself
  };

  const fullName = `${profileUser.firstName || ""} ${profileUser.lastName || ""}`.trim();

  return (
    <>
      <header className="profile-head">
        <Avatar src={profileUser.profilePicture} size={9} className="profile-avatar" />
        <div className="profile-info">
          <div className="profile-names">
            <h1>{fullName || profileUser.username}</h1>
            <p className="profile-handle">@{profileUser.username}</p>
          </div>
          <ul className="profile-stats">
            <li>
              <strong>{profileUser.postCount}</strong> {profileUser.postCount === 1 ? "post" : "posts"}
            </li>
            <li>
              <UserListModal url={`/api/users/${userId}/followers`} dataKey="followers" title="Followers" className="stat-btn">
                <strong>{profileUser.followerCount}</strong> {profileUser.followerCount === 1 ? "follower" : "followers"}
              </UserListModal>
            </li>
            <li>
              <UserListModal url={`/api/users/${userId}/following`} dataKey="following" title="Following" className="stat-btn">
                <strong>{profileUser.followingCount}</strong> following
              </UserListModal>
            </li>
          </ul>
          {!isMe && (
            <button
              type="button"
              className={`btn ${profileUser.isFollowedByMe ? "btn-secondary" : "btn-primary"}`}
              aria-pressed={profileUser.isFollowedByMe}
              onClick={() => handleFollow(!profileUser.isFollowedByMe)}
            >
              {profileUser.isFollowedByMe ? "Following" : "Follow"}
            </button>
          )}
        </div>
      </header>

      <h2 className="visually-hidden">Posts</h2>
      {profile.postIds.length === 0 ? (
        <StatusMessage
          title="No posts yet"
          message={isMe ? "Share your first photo with the New post button." : `${profileUser.username} has not shared anything yet.`}
        />
      ) : (
        <PostGrid postIds={profile.postIds} />
      )}
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

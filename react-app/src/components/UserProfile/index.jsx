import React from "react";
import { useParams } from "react-router";
import "./UserProfile.css";
import UserInfoBox from "./UserInfoBox";
import NotFound from "../NotFound";

const UserProfile = () => {
  const { userId } = useParams();
  // /:userId matches any single path segment, so /typo would land here.
  // Only numeric ids are profiles; anything else is a 404 page.
  if (!/^\d+$/.test(userId)) return <NotFound />;
  return (
    <div className="user-profile-papa-div">
      <UserInfoBox />
    </div>
  );
};

export default UserProfile;

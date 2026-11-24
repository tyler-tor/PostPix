import React, { useEffect, useState } from "react";
import { Modal } from "../../../context/Modal";
import { useSelector, useDispatch } from "react-redux";
import { getAllFollowers } from "../../../store/follower";
import UserFollowerList from "./UserFollowerList";
import { getProfileUser } from "../../../store/profileUser";

const UserFollowerListModal = ({ userId }) => {
  const followers = Object.values(useSelector((state) => state.followers));
  const [showModal, setShowModal] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [followNum, setFollowNum] = useState(0);
  const profileUser = useSelector(state => state.profileUser)
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getAllFollowers(userId)).then((res) => {
      if (res) {
        setFollowNum(res.length);
      }
    });
  }, [dispatch]);

  useEffect(() =>{
    dispatch(getProfileUser(userId))
  }, [dispatch])

  useEffect(() => {
    setFollowNum(followers.length);
  });

  const displayFollowers = () => {
    dispatch(getAllFollowers(userId)).then(() => {});
  };

  return (
    <>
      <a
        onClick={() => {
          setShowModal(!showModal);
          displayFollowers();
        }}
      >
        <strong>{profileUser.followerCount}</strong> followers
      </a>
      {showModal && (
        <Modal onClose={() => setShowModal(false)}>
          <UserFollowerList
            onClose={() => setShowModal(false)}
            followers={followers}
          />
        </Modal>
      )}
    </>
  );
};

export default UserFollowerListModal;

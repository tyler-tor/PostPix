import React, { useEffect, useState } from "react";
import { Modal } from "../../../context/Modal";
import { useSelector, useDispatch } from "react-redux";
import { getProfileFollowing } from "../../../store/profile_following_store";
import UserFollowingList from "./UserFollowingList";
import { getProfileUser } from "../../../store/profileUser";

const UserFollowingListModal = ({ userId }) => {
  const [showModal, setShowModal] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const following = Object.values(useSelector((state) => state.profileFollowing));
  const profileUser = useSelector(state => state.profileUser)
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(getProfileFollowing(userId));
  }, [dispatch, userId]);

  useEffect(() =>{
    dispatch(getProfileUser(userId))
  }, [dispatch])

  const displayFollowers = () => {
    dispatch(getProfileFollowing(userId));
  };

  return (
    <>
      <a
        onClick={() => {
          setShowModal(!showModal);
          displayFollowers();
        }}
      >
        <strong>{profileUser.followingCount}</strong>
        {' '}
        <span className="following-text-list">
        following
        </span>
      </a>
      {showModal && (
        <Modal onClose={() => setShowModal(false)}>
          <UserFollowingList
            onClose={() => setShowModal(false)}
            following={following}
          />
        </Modal>
      )}
    </>
  );
};

export default UserFollowingListModal;

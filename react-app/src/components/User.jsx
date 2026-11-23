import React, { useState, useEffect } from 'react';
import { useParams } from "react-router";
import apiFetch from "../utils/apiFetch";

function User() {
  const [user, setUser] = useState({});
  const { userId }  = useParams();

  useEffect(() => {
    if (!userId) {
      return;
    }
    (async () => {
      const response = await apiFetch(`/api/users/${userId}`);
      const user = await response.json();
      setUser(user);
    })();
  }, [userId]);

  if (!user) {
    return null;
  }

  return (
    <ul>
      <li>
        <strong>User Id</strong> {userId}
      </li>
      <li>
        <strong>Username</strong> {user.username}
      </li>
    </ul>
  );
}
export default User;

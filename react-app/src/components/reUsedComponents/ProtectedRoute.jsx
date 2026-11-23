import React from "react";
import { useSelector } from "react-redux";
import { Navigate, Outlet } from "react-router";

// Layout route: renders the matching child route (<Outlet />) for logged-in
// users and sends everyone else to the login page at "/".
const ProtectedRoute = () => {
  const user = useSelector((state) => state.session.user);
  return user ? <Outlet /> : <Navigate to="/" replace />;
};

export default ProtectedRoute;

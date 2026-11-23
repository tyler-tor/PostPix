import React, { useState, useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { useDispatch } from "react-redux";
import LoginPage from "./components/LoginPage";
import SignUpForm from "./components/LoginPage/SignUpForm";
import NavBar from "./components/NavBar";
import ProtectedRoute from "./components/reUsedComponents/ProtectedRoute";
import UsersList from "./components/UsersList";
// import User from "./components/User";
import TempFollow from "./components/TempFollow";
import TempPost from "./components/CreatePost/TempPost";
import TempComment from "./components/CreateComment/TempComment";
import { authenticate } from "./store/session";
import { useSelector } from "react-redux";
import HomeFeed from "./components/HomeFeed";
import UserProfile from "./components/UserProfile";
import ExplorePage from "./components/ExplorePage";
import NotFound from "./components/NotFound";

function App() {
  const [loaded, setLoaded] = useState(false);
  const user = useSelector((state) => state.session.user);
  const dispatch = useDispatch();

  useEffect(() => {
    (async () => {
      await dispatch(authenticate());
      setLoaded(true);
    })();
  }, [dispatch]);

  if (!loaded) {
    return null;
  }

  return (
    <BrowserRouter>
      {user && <NavBar />}
      <Routes>
        {/* "/" is the feed when logged in, the login page otherwise. */}
        <Route path="/" element={user ? <HomeFeed /> : <LoginPage />} />
        {/* Everything inside needs a logged-in user (see ProtectedRoute). */}
        <Route element={<ProtectedRoute />}>
          <Route path="/users" element={<UsersList />} />
          <Route path="/explore" element={<ExplorePage />} />
          {/* Static paths like /explore always win over this dynamic one. */}
          <Route path="/:userId" element={<UserProfile />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

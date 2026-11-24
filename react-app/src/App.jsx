import React, { lazy, Suspense, useState, useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { useDispatch, useSelector } from "react-redux";
import NavBar from "./components/NavBar";
import ProtectedRoute from "./components/reUsedComponents/ProtectedRoute";
import { authenticate } from "./store/session";

// Each page is its own chunk, downloaded when the route is first visited.
const LoginPage = lazy(() => import("./components/LoginPage"));
const HomeFeed = lazy(() => import("./components/HomeFeed"));
const UserProfile = lazy(() => import("./components/UserProfile"));
const ExplorePage = lazy(() => import("./components/ExplorePage"));
const NotFound = lazy(() => import("./components/NotFound"));

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
      <Suspense fallback={null}>
        <Routes>
          {/* "/" is the feed when logged in, the login page otherwise. */}
          <Route path="/" element={user ? <HomeFeed /> : <LoginPage />} />
          {/* Everything inside needs a logged-in user (see ProtectedRoute). */}
          <Route element={<ProtectedRoute />}>
            <Route path="/explore" element={<ExplorePage />} />
            {/* Static paths like /explore always win over this dynamic one. */}
            <Route path="/:userId" element={<UserProfile />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;

import React, { lazy, Suspense, useState, useEffect, useRef } from "react";
import { BrowserRouter, Route, Routes, useLocation } from "react-router";
import { useDispatch, useSelector } from "react-redux";
import NavBar from "./components/NavBar";
import Toaster from "./components/ui/Toaster";
import ProtectedRoute from "./components/reUsedComponents/ProtectedRoute";
import { authenticate } from "./store/session";

// Each page is its own chunk, downloaded when the route is first visited.
const LoginPage = lazy(() => import("./components/LoginPage"));
const HomeFeed = lazy(() => import("./components/HomeFeed"));
const UserProfile = lazy(() => import("./components/UserProfile"));
const ExplorePage = lazy(() => import("./components/ExplorePage"));
const NotFound = lazy(() => import("./components/NotFound"));

const TITLES = { "/": "Home", "/explore": "Explore" };

// On every page change: set the tab title and move keyboard/screen reader
// focus to the page content (a single-page app does not do this by itself).
// Skipped on the first load, where the browser has already done it.
const RouteEffects = ({ loggedIn }) => {
  const { pathname } = useLocation();
  const first = useRef(true);
  useEffect(() => {
    const name = pathname === "/" ? (loggedIn ? "Home" : "Log in") : TITLES[pathname] || (/^\/\d+$/.test(pathname) ? "Profile" : "Page not found");
    document.title = `${name} - Postpix`;
    if (first.current) {
      first.current = false;
      return;
    }
    document.getElementById("main")?.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }, [pathname, loggedIn]);
  return null;
};

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
      <a className="skip-link" href="#main">Skip to content</a>
      <RouteEffects loggedIn={!!user} />
      {user && <NavBar />}
      <main id="main" tabIndex={-1}>
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
      </main>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;

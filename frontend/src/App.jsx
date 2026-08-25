import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import { getTokens, setTokens } from "./api/client";
import Bookmarks from "./pages/Bookmarks.jsx";
import Courses from "./pages/Courses.jsx";
import CourseBooks from "./pages/CourseBooks.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Onboarding from "./pages/Onboarding.jsx";
import Profile from "./pages/Profile.jsx";
import Reader from "./pages/Reader.jsx";
import Stats from "./pages/Stats.jsx";

function RequireAuth() {
  if (!getTokens()) return <Navigate to="/onboarding" replace />;
  return <Layout />;
}

function RedirectIfAuthed({ children }) {
  if (getTokens()) return <Navigate to="/" replace />;
  return children;
}

function StartFresh() {
  setTokens(null);
  return <Navigate to="/onboarding" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/start" element={<StartFresh />} />
      <Route
        path="/onboarding"
        element={
          <RedirectIfAuthed>
            <Onboarding />
          </RedirectIfAuthed>
        }
      />
      <Route
        path="/login"
        element={
          <RedirectIfAuthed>
            <Login />
          </RedirectIfAuthed>
        }
      />
      <Route element={<RequireAuth />}>
        <Route path="/" element={<Home />} />
        <Route path="/bookmarks" element={<Bookmarks />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/courses/:langId" element={<CourseBooks />} />
        <Route path="/read/:bookId" element={<Reader />} />
        <Route path="/stats" element={<Stats />} />
        <Route path="/profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

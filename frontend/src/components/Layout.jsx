import { useEffect } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../store/auth";

const NAV_ITEMS = [
  { to: "/", label: "Asosiy", end: true },
  { to: "/bookmarks", label: "Xatcho'p" },
  { to: "/courses", label: "Kurslarim" },
  { to: "/stats", label: "Statistika" },
  { to: "/profile", label: "Profil" },
];

const PAGE_TITLES = {
  "/": "Asosiy",
  "/bookmarks": "Xatcho'p",
  "/courses": "Kurslarim",
  "/stats": "Statistika",
  "/profile": "Profil",
};

export default function Layout() {
  const location = useLocation();
  const user = useAuth((s) => s.user);
  const fetchUser = useAuth((s) => s.fetchUser);

  useEffect(() => {
    if (!user) {
      fetchUser().catch(() => {});
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  let title = PAGE_TITLES[location.pathname] || "";
  if (location.pathname.startsWith("/read/")) title = "O'qish rejimi";
  else if (/^\/courses\/\d+/.test(location.pathname)) title = "Kurslarim";

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((w) => w[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()
    : "?";

  return (
    <div className="app-shell">
      <aside className="sidebar glass">
        <NavLink to="/" className="logo">
          LINGUO
        </NavLink>
        <nav className="side-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `side-link${isActive ? " active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          Muddatsiz. Bosimsiz.
          <br />
          O'z tezligingizda.
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar glass">
          <h1 className="topbar-title">{title}</h1>
          <div className="topbar-user">
            <span className="avatar">{initials}</span>
            <span className="user-name">{user?.name || "..."}</span>
          </div>
        </header>
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

import type { ReactNode } from "react";
import { useEffect, useState } from "react";

type DashboardPage = {
  id: string;
  label: string;
  component: ReactNode;
};

type DashboardLayoutProps = {
  pages: readonly DashboardPage[];
};

export function DashboardLayout({ pages }: DashboardLayoutProps) {
  const pageIds = pages.map((page) => page.id);
  const defaultPageId = pages[0]?.id ?? "overview";
  const hashPageId = window.location.hash.replace("#", "");
  const [activePageId, setActivePageId] = useState(pageIds.includes(hashPageId) ? hashPageId : defaultPageId);
  const activePage = pages.find((page) => page.id === activePageId) ?? pages[0];

  useEffect(() => {
    function handleHashChange() {
      const nextPageId = window.location.hash.replace("#", "");
      if (pageIds.includes(nextPageId)) {
        setActivePageId(nextPageId);
      }
    }

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, [pageIds]);

  function navigate(pageId: string) {
    setActivePageId(pageId);
    window.history.replaceState(null, "", `#${pageId}`);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-row">
            <span className="brand-monogram" role="img" aria-label="LoanScore">
              <svg width="24" height="24" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <defs>
                  <linearGradient id="mvShieldGrad" x1="4" y1="4" x2="28" y2="30" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stopColor="#1f6f78" />
                    <stop offset="100%" stopColor="#0f1f3d" />
                  </linearGradient>
                </defs>
                <path
                  d="M16 2.4 L27.2 7.6 V15.6 C27.2 22.9 22.1 28.3 16 30.4 C9.9 28.3 4.8 22.9 4.8 15.6 V7.6 Z"
                  fill="url(#mvShieldGrad)"
                  stroke="#f2cb66"
                  strokeWidth="1"
                  strokeLinejoin="round"
                />
                <polyline
                  points="8.5,19 11.5,19 13.6,12.8 16.2,22.4 18.2,16.6 20.4,16.6 23.5,16.6"
                  fill="none"
                  stroke="#f2cb66"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <circle cx="13.6" cy="12.8" r="1.15" fill="#f2cb66" />
                <circle cx="16" cy="24.2" r="1.7" fill="#f2cb66" opacity="0.92" />
                <path d="M14.5 24.7 L17.5 24.7 L16 27.6 Z" fill="#f2cb66" opacity="0.92" />
              </svg>
            </span>
            <p className="eyebrow" style={{ margin: 0 }}>LoanScore</p>
          </div>
          <h1>Credit Risk Monitor</h1>
        </div>
        <nav className="nav-list" aria-label="Dashboard sections">
          {pages.map((page) => (
            <button
              className={page.id === activePage.id ? "nav-item active" : "nav-item"}
              key={page.id}
              onClick={() => navigate(page.id)}
              type="button"
            >
              {page.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span>FastAPI backend</span>
          <strong>Production reliability workflow</strong>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div>
            <span>Dashboard</span>
            <strong>{activePage.label}</strong>
          </div>
          <div className="topbar-pill">Credit risk MVP</div>
        </header>
        <main className="content">{activePage.component}</main>
        <footer className="app-footer">
          Rayen Lassoued | github.com/rayenx2 | linkedin.com/in/Rayen-Lassoued
        </footer>
      </div>
    </div>
  );
}

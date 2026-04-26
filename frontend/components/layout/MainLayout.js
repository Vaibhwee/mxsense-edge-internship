"use client";

import { useEffect, useState } from "react";

import Sidebar from "./Sidebar";

export default function MainLayout({
  brand,
  modules,
  activeModuleSlug,
  activeModuleTitle,
  children,
  isDataModule: _isDataModule,
}) {
  const [navOpen, setNavOpen] = useState(false);

  useEffect(() => {
    function onKeyDown(e) {
      if (e.key === "Escape") setNavOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 769px)");
    function onChange() {
      if (mq.matches) setNavOpen(false);
    }
    mq.addEventListener("change", onChange);
    onChange();
    return () => mq.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    document.body.classList.toggle("sidebar-drawer-open", navOpen);
    return () => document.body.classList.remove("sidebar-drawer-open");
  }, [navOpen]);

  return (
    <main className="slide-page dashboard-shell">
      <section className="console-stage">
        <div className="console-header">
          <div className="header-brand">
            <button
              type="button"
              className="sidebar-toggle"
              aria-expanded={navOpen}
              aria-controls="console-module-nav"
              onClick={() => setNavOpen((v) => !v)}
            >
              <span className="sidebar-toggle-bars" aria-hidden="true" />
              <span className="sr-only">Toggle navigation menu</span>
            </button>
            <span className="header-badge">{activeModuleTitle}</span>
            <h1>{brand}</h1>
          </div>
          <form action="/auth/sign-out" method="post">
            <button className="ui-button ui-button-rect signout-button" type="submit">
              Sign out
            </button>
          </form>
        </div>

        <div className={`console-layout${navOpen ? " has-drawer-open" : ""}`}>
          {navOpen ? (
            <button
              type="button"
              className="sidebar-backdrop"
              aria-label="Close menu"
              tabIndex={-1}
              onClick={() => setNavOpen(false)}
            />
          ) : null}
          <Sidebar
            modules={modules}
            activeModuleSlug={activeModuleSlug}
            id="console-module-nav"
            isOpen={navOpen}
            onNavigate={() => setNavOpen(false)}
          />
          <section className="console-main">
            <div className="content-container">{children}</div>
          </section>
        </div>
      </section>
    </main>
  );
}

"use client";

import Link from "next/link";
import { useMemo } from "react";
import { usePathname } from "next/navigation";

function deriveActiveSlug(pathname, activeModuleSlug) {
  if (!pathname) return activeModuleSlug;

  if (pathname.startsWith("/dashboard/device-management/actions/")) {
    return "device-management";
  }

  if (pathname.startsWith("/dashboard/modules/")) {
    const parts = pathname.split("/").filter(Boolean);
    return parts[2] || activeModuleSlug;
  }

  if (pathname.startsWith("/device-management")) return "device-management";
  if (pathname.startsWith("/adaptation")) return "adaptation";
  if (pathname.startsWith("/locations")) return "locations";
  if (pathname.startsWith("/dashboard")) return "dashboard";

  if (pathname.startsWith("/modules/")) {
    const parts = pathname.split("/").filter(Boolean);
    return parts[1] || activeModuleSlug;
  }

  return activeModuleSlug;
}

function moduleHref(slug) {
  if (slug === "dashboard") return "/dashboard";
  if (slug === "device-management") return "/device-management";
  if (slug === "adaptation") return "/adaptation";
  return `/dashboard/modules/${slug}`;
}

export default function Sidebar({
  modules,
  activeModuleSlug,
  id,
  isOpen = false,
  onNavigate,
}) {
  const pathname = usePathname();
  const resolvedActiveSlug = useMemo(
    () => deriveActiveSlug(pathname, activeModuleSlug),
    [pathname, activeModuleSlug]
  );

  const asideClass = ["console-sidebar", "sidebar-interactive", isOpen ? "is-open" : ""]
    .filter(Boolean)
    .join(" ");

  return (
    <aside className={asideClass} id={id}>
      <div className="sidebar-title">Modules</div>
      <nav className="module-nav" aria-label="Module navigation">
        {modules.map((module) => (
          <Link
            className={
              module.slug === resolvedActiveSlug
                ? "ui-button ui-button-rect module-link sidebar-nav-link active"
                : "ui-button ui-button-rect module-link sidebar-nav-link"
            }
            href={moduleHref(module.slug)}
            key={module.slug}
            onClick={() => onNavigate?.()}
          >
            {module.title}
          </Link>
        ))}

        <Link
          className={
            resolvedActiveSlug === "locations"
              ? "ui-button ui-button-rect module-link sidebar-nav-link active"
              : "ui-button ui-button-rect module-link sidebar-nav-link"
          }
          href="/locations"
          onClick={() => onNavigate?.()}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z"
              stroke="currentColor"
              strokeWidth="2"
              opacity="0.9"
            />
            <path
              d="M2 12H22"
              stroke="currentColor"
              strokeWidth="2"
              opacity="0.7"
            />
            <path
              d="M12 2C14.5 4.8 16 8.3 16 12C16 15.7 14.5 19.2 12 22C9.5 19.2 8 15.7 8 12C8 8.3 9.5 4.8 12 2Z"
              stroke="currentColor"
              strokeWidth="2"
              opacity="0.7"
            />
          </svg>
          <span>Locations</span>
        </Link>
      </nav>
    </aside>
  );
}

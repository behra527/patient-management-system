
"use client";

import Link from "next/link";

type AppSidebarProps = {
  onNavigateToPatients: () => void;
  onNavigateToAppointments: () => void;
  onNavigateToBilling: () => void;
};

export default function AppSidebar({
  onNavigateToPatients,
  onNavigateToAppointments,
  onNavigateToBilling,
}: AppSidebarProps) {
  return (
    <aside className="sidebar">
      <Link href="/" className="brand">
        <div
          className="brand-icon-wrapper"
          aria-hidden="true"
          style={{
            background:
              "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
            padding: "10px",
            borderRadius: "10px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 4px 12px rgba(2, 132, 199, 0.25)",
          }}
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#ffffff"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <span
            style={{
              fontSize: "18px",
              fontWeight: 700,
              letterSpacing: "-0.02em",
              color: "#ffffff",
              lineHeight: 1.2,
            }}
          >
            AuraHealth
          </span>

          <span
            style={{
              fontSize: "11px",
              fontWeight: 600,
              color: "#38bdf8",
              letterSpacing: "0.05em",
              textTransform: "uppercase",
            }}
          >
            Clinical Intelligence
          </span>
        </div>
      </Link>

      <div className="nav-label" style={{ color: "#94a3b8" }}>
        WORKSPACE
      </div>

      <nav className="navigation" aria-label="Main navigation">
        <Link href="/" className="nav-item active" aria-current="page">
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="14" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
          </svg>
          Dashboard
        </Link>

        <button
          type="button"
          className="nav-item"
          onClick={onNavigateToPatients}
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          Patient Directory
        </button>
        <button type="button" className="nav-item" onClick={onNavigateToAppointments}>
          Appointments
        </button>
        <button type="button" className="nav-item" onClick={onNavigateToBilling}>
          Billing Management
        </button>
        <Link href="/doctors" className="nav-item">
          Doctors Management
        </Link>
        <Link href="/vitals" className="nav-item">
          Patient Vitals
        </Link>
      </nav>

      <div className="sidebar-bottom">
        <div
          className="help-card"
          style={{
            background: "rgba(255, 255, 255, 0.05)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            borderRadius: "10px",
            padding: "14px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              color: "#38bdf8",
              marginBottom: "4px",
              fontSize: "13px",
              fontWeight: 600,
            }}
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            Security Notice
          </div>

          <p style={{ margin: 0, fontSize: "12px", color: "#cbd5e1" }}>
            Patient records are managed through the connected API.
          </p>
        </div>

        <div
          className="profile"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            marginTop: "16px",
          }}
        >
          <div
            className="avatar"
            style={{
              background: "#38bdf8",
              color: "#0f172a",
              fontWeight: 700,
              width: "36px",
              height: "36px",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            aria-hidden="true"
          >
            AH
          </div>

          <div>
            <strong
              style={{
                fontSize: "13px",
                color: "#ffffff",
                display: "block",
              }}
            >
              AuraHealth User
            </strong>

            <small
              style={{
                fontSize: "11px",
                color: "#94a3b8",
                display: "block",
              }}
            >
              Clinical Workspace
            </small>
          </div>
        </div>
      </div>
    </aside>
  );
}




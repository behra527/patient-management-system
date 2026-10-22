"use client";

import type { AppointmentStatus } from "@/lib/api";

type Props = { status: AppointmentStatus };

const colors: Record<AppointmentStatus, { background: string; color: string }> = {
  Scheduled: { background: "#dbeafe", color: "#1d4ed8" },
  Completed: { background: "#dcfce7", color: "#166534" },
  Cancelled: { background: "#fee2e2", color: "#991b1b" },
};

export default function AppointmentStatusBadge({ status }: Props) {
  return (
    <span style={{
      ...colors[status],
      display: "inline-block",
      padding: "4px 9px",
      borderRadius: "999px",
      fontSize: "12px",
      fontWeight: 600,
      whiteSpace: "nowrap",
    }}>
      {status}
    </span>
  );
}

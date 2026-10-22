"use client";

import type { AppointmentStatus } from "@/lib/api";

type Props = {
  status: AppointmentStatus | "";
  onChange: (status: AppointmentStatus | "") => void;
};

export default function AppointmentFilters({ status, onChange }: Props) {
  return (
    <label style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
      <span style={{ fontSize: 13, color: "#475569" }}>Filter by status</span>
      <select
        value={status}
        onChange={(event) => onChange(event.target.value as AppointmentStatus | "")}
        style={{ padding: "9px 12px", border: "1px solid #cbd5e1", borderRadius: 8, background: "#fff" }}
      >
        <option value="">All appointments</option>
        <option value="Scheduled">Scheduled</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
    </label>
  );
}

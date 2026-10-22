"use client";

import type { Appointment, AppointmentStatus } from "@/lib/api";
import AppointmentStatusBadge from "./AppointmentStatusBadge";

type Props = {
  appointments: Appointment[];
  loading: boolean;
  onStatusChange: (id: number, status: AppointmentStatus) => void;
  updatingId: number | null;
};

const cellStyle: React.CSSProperties = {
  padding: "13px 12px",
  textAlign: "left",
  borderBottom: "1px solid #e2e8f0",
  fontSize: 13,
  verticalAlign: "top",
};

export default function AppointmentList({
  appointments,
  loading,
  onStatusChange,
  updatingId,
}: Props) {
  if (loading) return <p style={{ color: "#64748b" }}>Loading appointments...</p>;

  if (appointments.length === 0) {
    return (
      <div style={{ padding: 28, textAlign: "center", color: "#64748b" }}>
        No appointments found. Create an appointment to get started.
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#f8fafc" }}>
            {["ID", "Patient ID", "Doctor ID", "Date & time", "Duration", "Reason", "Status", "Update status"].map((heading) => (
              <th key={heading} style={cellStyle}>{heading}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {appointments.map((appointment) => (
            <tr key={appointment.id}>
              <td style={cellStyle}>APT-{appointment.id}</td>
              <td style={cellStyle}>{appointment.patient_id}</td>
              <td style={cellStyle}>{appointment.doctor_id}</td>
              <td style={cellStyle}>
                {appointment.appointment_date}
                <br />
                {appointment.appointment_time.slice(0, 5)}
              </td>
              <td style={cellStyle}>{appointment.duration_minutes} min</td>
              <td style={{ ...cellStyle, minWidth: 160 }}>{appointment.reason}</td>
              <td style={cellStyle}><AppointmentStatusBadge status={appointment.status} /></td>
              <td style={cellStyle}>
                {appointment.status === "Scheduled" ? (
                  <select
                    aria-label={`Update appointment ${appointment.id} status`}
                    value=""
                    disabled={updatingId === appointment.id}
                    onChange={(event) => {
                      const value = event.target.value as AppointmentStatus;
                      if (value) onStatusChange(appointment.id, value);
                    }}
                    style={{ padding: 7, border: "1px solid #cbd5e1", borderRadius: 6 }}
                  >
                    <option value="">Change...</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                  </select>
                ) : (
                  <span style={{ color: "#64748b" }}>Final status</span>
                )}
                {updatingId === appointment.id && <small> Saving...</small>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

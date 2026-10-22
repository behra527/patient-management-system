"use client";

import { useState, type FormEvent } from "react";
import type { AppointmentPayload, Doctor, Patient } from "@/lib/api";

type Props = {
  patients: Patient[];
  doctors: Doctor[];
  saving: boolean;
  error: string;
  onSubmit: (payload: AppointmentPayload) => Promise<void>;
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  padding: "10px 12px",
  border: "1px solid #cbd5e1",
  borderRadius: 8,
  background: "#fff",
  color: "#0f172a",
};

const labelStyle: React.CSSProperties = {
  display: "grid",
  gap: 6,
  color: "#334155",
  fontSize: 13,
  fontWeight: 600,
};

export default function AppointmentForm({
  patients,
  doctors,
  saving,
  error,
  onSubmit,
}: Props) {
  const [patientId, setPatientId] = useState("");
  const [doctorId, setDoctorId] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [duration, setDuration] = useState("30");
  const [reason, setReason] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    await onSubmit({
      patient_id: Number(patientId),
      doctor_id: Number(doctorId),
      appointment_date: date,
      appointment_time: time,
      duration_minutes: Number(duration),
      reason: reason.trim(),
    });

    setPatientId("");
    setDoctorId("");
    setDate("");
    setTime("");
    setDuration("30");
    setReason("");
  }

  return (
    <form onSubmit={handleSubmit} style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
      gap: 16,
      padding: 20,
      border: "1px solid #e2e8f0",
      borderRadius: 12,
      background: "#fff",
      marginBottom: 22,
    }}>
      <label style={labelStyle}>
        Patient *
        <select required value={patientId} onChange={(e) => setPatientId(e.target.value)} style={inputStyle}>
          <option value="">Select patient</option>
          {patients.map((patient) => (
            <option key={patient.id} value={patient.id}>
              {patient.full_name} (ID: {patient.id})
            </option>
          ))}
        </select>
      </label>

      <label style={labelStyle}>
        Active doctor *
        <select required value={doctorId} onChange={(e) => setDoctorId(e.target.value)} style={inputStyle}>
          <option value="">Select doctor</option>
          {doctors.filter((doctor) => doctor.status === "Active").map((doctor) => (
            <option key={doctor.id} value={doctor.id}>
              {doctor.full_name} (ID: {doctor.id})
            </option>
          ))}
        </select>
      </label>

      <label style={labelStyle}>
        Appointment date *
        <input required type="date" min={new Date().toLocaleDateString("en-CA")} value={date} onChange={(e) => setDate(e.target.value)} style={inputStyle} />
      </label>

      <label style={labelStyle}>
        Appointment time *
        <input required type="time" step={60} value={time} onChange={(e) => setTime(e.target.value)} style={inputStyle} />
      </label>

      <label style={labelStyle}>
        Duration *
        <select value={duration} onChange={(e) => setDuration(e.target.value)} style={inputStyle}>
          {[15, 30, 45, 60, 90, 120].map((minutes) => (
            <option key={minutes} value={minutes}>{minutes} minutes</option>
          ))}
        </select>
      </label>

      <label style={{ ...labelStyle, gridColumn: "1 / -1" }}>
        Reason for visit *
        <textarea required minLength={3} maxLength={500} value={reason} onChange={(e) => setReason(e.target.value)} rows={3} placeholder="Enter reason for consultation" style={{ ...inputStyle, resize: "vertical" }} />
      </label>

      {error && (
        <p role="alert" style={{ gridColumn: "1 / -1", color: "#b91c1c", margin: 0 }}>
          {error}
        </p>
      )}

      <div style={{ gridColumn: "1 / -1" }}>
        <button type="submit" disabled={saving || patients.length === 0 || doctors.every((doctor) => doctor.status !== "Active")} style={{
          padding: "11px 18px",
          border: 0,
          borderRadius: 8,
          background: "#0369a1",
          color: "#fff",
          fontWeight: 600,
          cursor: saving ? "wait" : "pointer",
          opacity: saving ? 0.7 : 1,
        }}>
          {saving ? "Creating appointment..." : "Create appointment"}
        </button>
      </div>
    </form>
  );
}

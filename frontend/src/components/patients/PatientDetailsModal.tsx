"use client";

import type { Patient } from "@/lib/api";

type PatientDetailsModalProps = {
  patient: Patient | null;
  onClose: () => void;
};

export default function PatientDetailsModal({
  patient,
  onClose,
}: PatientDetailsModalProps) {
  if (!patient) {
    return null;
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(15, 23, 42, 0.5)",
        display: "grid",
        placeItems: "center",
        zIndex: 1000,
        padding: "16px",
      }}
    >
      <div
        style={{
          background: "#ffffff",
          width: "100%",
          maxWidth: "440px",
          borderRadius: "16px",
          padding: "24px",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
        }}
      >
        <h2
          style={{
            marginTop: 0,
            fontSize: "20px",
            color: "#0f172a",
          }}
        >
          Patient Profile
        </h2>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            margin: "20px 0",
            fontSize: "14px",
            overflowWrap: "anywhere",
          }}
        >
          <div>
            <strong>Name:</strong> {patient.full_name}
          </div>
          <div>
            <strong>Gender:</strong> {patient.gender}
          </div>
          <div>
            <strong>Date of Birth:</strong> {patient.date_of_birth}
          </div>
          <div>
            <strong>Phone:</strong> {patient.phone || "Not provided"}
          </div>
          <div>
            <strong>Email:</strong> {patient.email || "Not provided"}
          </div>
          <div>
            <strong>Address:</strong> {patient.address || "Not provided"}
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: "10px 16px",
              background: "#0f172a",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

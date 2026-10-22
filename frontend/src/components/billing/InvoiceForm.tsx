"use client";

import { useState, type FormEvent } from "react";
import type {
  Appointment,
  InvoicePayload,
  Patient,
} from "@/lib/api";

type InvoiceFormProps = {
  patients: Patient[];
  appointments: Appointment[];
  saving: boolean;
  error: string;
  onSubmit: (payload: InvoicePayload) => Promise<void>;
};

function todayLocal(): string {
  const date = new Date();
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function InvoiceForm({
  patients,
  appointments,
  saving,
  error,
  onSubmit,
}: InvoiceFormProps) {
  const [invoiceNumber, setInvoiceNumber] = useState("");
  const [patientId, setPatientId] = useState("");
  const [appointmentId, setAppointmentId] = useState("");
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [dueDate, setDueDate] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const amountPkr = Number(amount);

    if (!Number.isFinite(amountPkr) || amountPkr <= 0) {
      return;
    }

    await onSubmit({
      invoice_number: invoiceNumber.trim(),
      patient_id: Number(patientId),
      appointment_id: appointmentId ? Number(appointmentId) : null,
      description: description.trim(),
      total_amount_paisa: Math.round(amountPkr * 100),
      due_date: dueDate,
    });

    setInvoiceNumber("");
    setPatientId("");
    setAppointmentId("");
    setDescription("");
    setAmount("");
    setDueDate("");
  }

  return (
    <section className="billing-form-section">
      <div className="section-heading">
        <div>
          <h2>Create Invoice</h2>
          <p>Generate a bill for a registered patient.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="billing-form">
        {error && (
          <p role="alert" className="form-error">
            {error}
          </p>
        )}

        <div className="form-grid">
          <label>
            Invoice Number
            <input
              value={invoiceNumber}
              onChange={(event) => setInvoiceNumber(event.target.value)}
              minLength={3}
              maxLength={50}
              required
              placeholder="e.g. INV-2026-001"
            />
          </label>

          <label>
            Patient
            <select
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              required
            >
              <option value="">Select patient</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.full_name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Related Appointment (Optional)
            <select
              value={appointmentId}
              onChange={(event) => setAppointmentId(event.target.value)}
            >
              <option value="">No appointment linked</option>
              {appointments
                .filter(
                  (appointment) =>
                    !patientId ||
                    appointment.patient_id === Number(patientId),
                )
                .map((appointment) => (
                  <option key={appointment.id} value={appointment.id}>
                    Appointment #{appointment.id} — {appointment.appointment_date}
                  </option>
                ))}
            </select>
          </label>

          <label>
            Total Amount (PKR)
            <input
              type="number"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              min="0.01"
              step="0.01"
              required
              placeholder="e.g. 2500.00"
            />
          </label>

          <label>
            Due Date
            <input
              type="date"
              value={dueDate}
              onChange={(event) => setDueDate(event.target.value)}
              min={todayLocal()}
              required
            />
          </label>

          <label className="form-full-width">
            Description
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              minLength={3}
              maxLength={500}
              required
              rows={3}
              placeholder="Consultation, laboratory tests, or treatment"
            />
          </label>
        </div>

        <button type="submit" disabled={saving || patients.length === 0}>
          {saving ? "Creating Invoice..." : "Create Invoice"}
        </button>
      </form>
    </section>
  );
}

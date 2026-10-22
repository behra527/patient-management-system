"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  createDoctor,
  deactivateDoctor,
  getDoctors,
  hasAccessToken,
  updateDoctor,
  type Doctor,
  type DoctorPayload,
  type DoctorStatus,
} from "@/lib/api";

const emptyForm: DoctorPayload = {
  full_name: "",
  specialty: "",
  email: "",
  phone: "",
  license_number: "",
  status: "Active",
};

export default function DoctorsPage() {
  const router = useRouter();
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [form, setForm] = useState<DoctorPayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const loadDoctors = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setDoctors(await getDoctors());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load doctors.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/");
      return;
    }
    void loadDoctors();
  }, [router, loadDoctors]);

  function changeField(
    field: keyof DoctorPayload,
    value: string,
  ) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function startEdit(doctor: Doctor) {
    setEditingId(doctor.id);
    setForm({
      full_name: doctor.full_name,
      specialty: doctor.specialty,
      email: doctor.email,
      phone: doctor.phone ?? "",
      license_number: doctor.license_number,
      status: doctor.status,
    });
    setMessage("");
    setError("");
  }

  function resetForm() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function submitForm(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      const payload: DoctorPayload = {
        ...form,
        full_name: form.full_name.trim(),
        specialty: form.specialty.trim(),
        email: form.email.trim(),
        phone: form.phone?.trim() || null,
        license_number: form.license_number.trim(),
      };

      if (editingId !== null) {
        await updateDoctor(editingId, payload);
        setMessage("Doctor updated.");
      } else {
        await createDoctor(payload);
        setMessage("Doctor created.");
      }

      resetForm();
      await loadDoctors();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save doctor.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeactivate(doctor: Doctor) {
    if (!window.confirm(`Deactivate ${doctor.full_name}?`)) return;

    setError("");
    setMessage("");
    try {
      await deactivateDoctor(doctor.id);
      setMessage("Doctor deactivated.");
      await loadDoctors();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not deactivate doctor.");
    }
  }

  return (
    <main className="clinic-module-page doctors-page">
      <header className="clinic-page-header">
        <div>
          <h1 className="clinic-page-title">Doctors</h1>
          <p className="clinic-page-subtitle">
            Manage doctor profiles using the connected API.
          </p>
        </div>
        <button
          className="clinic-button clinic-button-secondary"
          onClick={() => router.push("/")}
        >
          Dashboard
        </button>
      </header>

      {message && <p role="status" className="clinic-alert clinic-alert-success">{message}</p>}
      {error && <p role="alert" className="clinic-alert clinic-alert-error">{error}</p>}

      <section className="clinic-panel">
        <h2 className="clinic-section-title">
          {editingId !== null ? "Edit Doctor" : "Register Doctor"}
        </h2>

        <form onSubmit={submitForm} className="clinic-form-grid">
          <label className="clinic-field">
            Full name
            <input className="clinic-input" required minLength={2} maxLength={100}
              value={form.full_name} onChange={(e) => changeField("full_name", e.target.value)} />
          </label>
          <label className="clinic-field">
            Specialty
            <input className="clinic-input" required minLength={2} maxLength={100}
              value={form.specialty} onChange={(e) => changeField("specialty", e.target.value)} />
          </label>
          <label className="clinic-field">
            Email
            <input className="clinic-input" type="email" required
              value={form.email} onChange={(e) => changeField("email", e.target.value)} />
          </label>
          <label className="clinic-field">
            Phone
            <input className="clinic-input" maxLength={20}
              value={form.phone ?? ""} onChange={(e) => changeField("phone", e.target.value)} />
          </label>
          <label className="clinic-field">
            License number
            <input className="clinic-input" required minLength={2} maxLength={50}
              value={form.license_number} onChange={(e) => changeField("license_number", e.target.value)} />
          </label>
          <label className="clinic-field">
            Status
            <select className="clinic-input" value={form.status}
              onChange={(e) => changeField("status", e.target.value as DoctorStatus)}>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="On Leave">On Leave</option>
            </select>
          </label>
          <div className="clinic-form-actions">
            <button disabled={saving} className="clinic-button clinic-button-primary">
              {saving ? "Saving..." : editingId !== null ? "Update Doctor" : "Create Doctor"}
            </button>
            {editingId !== null && (
              <button type="button" className="clinic-button clinic-button-secondary" onClick={resetForm}>
                Cancel
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="clinic-panel clinic-table-panel">
        <div className="clinic-table-toolbar">
          <h2 className="clinic-section-title">Doctor Directory</h2>
          <button className="clinic-button clinic-button-secondary" onClick={() => void loadDoctors()}>
            Refresh
          </button>
        </div>
        {loading ? <p className="p-4">Loading doctors...</p> : (
          <table className="clinic-table">
            <thead className="clinic-table-head">
              <tr>
                <th className="clinic-table-cell">Name</th>
                <th className="clinic-table-cell">Specialty</th>
                <th className="clinic-table-cell">Email</th>
                <th className="clinic-table-cell">License</th>
                <th className="clinic-table-cell">Status</th>
                <th className="clinic-table-cell">Actions</th>
              </tr>
            </thead>
            <tbody>
              {doctors.map((doctor) => (
                <tr key={doctor.id} className="clinic-table-row">
                  <td className="clinic-table-cell">{doctor.full_name}</td>
                  <td className="clinic-table-cell">{doctor.specialty}</td>
                  <td className="clinic-table-cell">{doctor.email}</td>
                  <td className="clinic-table-cell">{doctor.license_number}</td>
                  <td className="clinic-table-cell">{doctor.status}</td>
                  <td className="flex flex-wrap gap-2 clinic-table-cell">
                    <button className="clinic-button clinic-button-secondary" onClick={() => startEdit(doctor)}>Edit</button>
                    {doctor.status !== "Inactive" && (
                      <button className="clinic-button clinic-button-danger"
                        onClick={() => void handleDeactivate(doctor)}>Deactivate</button>
                    )}
                  </td>
                </tr>
              ))}
              {doctors.length === 0 && (
                <tr><td className="p-4" colSpan={6}>No doctors found.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}



"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getPatients,
  getPatientVitals,
  getPatientVitalsSummary,
  createVitals,
  hasAccessToken,
  type Patient,
  type VitalsRecord,
  type VitalsSummary,
} from "@/lib/api";

export default function VitalsPage() {
  const router = useRouter();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [patientId, setPatientId] = useState("");
  const [age, setAge] = useState("30");
  const [systolic, setSystolic] = useState("120");
  const [diastolic, setDiastolic] = useState("80");
  const [glucose, setGlucose] = useState("5.5");
  const [records, setRecords] = useState<VitalsRecord[]>([]);
  const [summary, setSummary] = useState<VitalsSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!hasAccessToken()) {
      router.replace("/");
      return;
    }

    getPatients()
      .then((items) => {
        setPatients(items);
        if (items.length) setPatientId(String(items[0].id));
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "Could not load patients.");
      });
  }, [router]);

  const loadHistory = useCallback(async (id: string) => {
    if (!id) {
      setRecords([]);
      setSummary(null);
      return;
    }

    setLoading(true);
    setError("");
    try {
      const [history, totals] = await Promise.all([
        getPatientVitals(id),
        getPatientVitalsSummary(id),
      ]);
      setRecords(history);
      setSummary(totals);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load vitals history.");
      setRecords([]);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (patientId) void loadHistory(patientId);
  }, [patientId, loadHistory]);

  async function submitVitals(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    try {
      await createVitals({
        patient_id: patientId,
        age: Number(age),
        blood_pressure: {
          systolic: Number(systolic),
          diastolic: Number(diastolic),
        },
        glucose_level: Number(glucose),
      });
      setMessage("Vitals record saved.");
      await loadHistory(patientId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save vitals.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="clinic-module-page vitals-page">
      <header className="clinic-page-header">
        <div>
          <h1 className="clinic-page-title">Vitals &amp; Health Metrics</h1>
          <p className="clinic-page-subtitle">
            Record and review patient blood pressure and glucose measurements.
          </p>
        </div>
        <button className="clinic-button clinic-button-secondary" onClick={() => router.push("/")}>
          Dashboard
        </button>
      </header>

      {message && <p role="status" className="clinic-alert clinic-alert-success">{message}</p>}
      {error && <p role="alert" className="clinic-alert clinic-alert-error">{error}</p>}

      <section className="clinic-panel">
        <h2 className="clinic-section-title">Record Patient Vitals</h2>
        <form onSubmit={submitVitals} className="clinic-form-grid">
          <label className="clinic-field">
            Patient
            <select className="clinic-input" required value={patientId}
              onChange={(e) => setPatientId(e.target.value)}>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.full_name} (ID: {patient.id})
                </option>
              ))}
            </select>
          </label>
          <label className="clinic-field">
            Age (years)
            <input className="clinic-input" type="number" min={0} max={120}
              required value={age} onChange={(e) => setAge(e.target.value)} />
          </label>
          <label className="clinic-field">
            Systolic blood pressure (50–300)
            <input className="clinic-input" type="number" min={50} max={300}
              required value={systolic} onChange={(e) => setSystolic(e.target.value)} />
          </label>
          <label className="clinic-field">
            Diastolic blood pressure (30–200)
            <input className="clinic-input" type="number" min={30} max={200}
              required value={diastolic} onChange={(e) => setDiastolic(e.target.value)} />
          </label>
          <label className="clinic-field">
            Glucose level
            <input className="clinic-input" type="number" min="0.01" step="any"
              required value={glucose} onChange={(e) => setGlucose(e.target.value)} />
          </label>
          <div className="clinic-form-actions">
            <button disabled={saving || !patientId || patients.length === 0}
              className="clinic-button clinic-button-primary">
              {saving ? "Saving..." : "Save Vitals"}
            </button>
          </div>
        </form>
      </section>

      <section className="clinic-panel">
        <div className="mb-4 clinic-page-header">
          <h2 className="clinic-section-title">Patient Vitals Summary</h2>
          <button className="clinic-button clinic-button-secondary" disabled={!patientId || loading}
            onClick={() => void loadHistory(patientId)}>Refresh</button>
        </div>

        {loading && <p>Loading vitals...</p>}

        {summary && (
          <div className="grid gaclinic-table-cell sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg clinic-table-head p-4">
              <p className="clinic-stat-label">Total records</p>
              <p className="clinic-stat-value">{summary.total_records}</p>
            </div>
            <div className="rounded-lg clinic-table-head p-4">
              <p className="clinic-stat-label">Average systolic</p>
              <p className="clinic-stat-value">{summary.average_systolic.toFixed(1)}</p>
            </div>
            <div className="rounded-lg clinic-table-head p-4">
              <p className="clinic-stat-label">Average diastolic</p>
              <p className="clinic-stat-value">{summary.average_diastolic.toFixed(1)}</p>
            </div>
            <div className="rounded-lg clinic-table-head p-4">
              <p className="clinic-stat-label">Average glucose</p>
              <p className="clinic-stat-value">{summary.average_glucose_level.toFixed(2)}</p>
            </div>
          </div>
        )}

        <h3 className="clinic-subsection-title">Measurement History</h3>
        <div className="clinic-table-scroll">
          <table className="clinic-table">
            <thead className="clinic-table-head">
              <tr>
                <th className="clinic-table-cell">Recorded at</th>
                <th className="clinic-table-cell">Blood pressure</th>
                <th className="clinic-table-cell">Glucose</th>
                <th className="clinic-table-cell">Age</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id} className="clinic-table-row">
                  <td className="clinic-table-cell">{new Date(record.recorded_at).toLocaleString()}</td>
                  <td className="clinic-table-cell">{record.blood_pressure.systolic}/{record.blood_pressure.diastolic}</td>
                  <td className="clinic-table-cell">{record.glucose_level}</td>
                  <td className="clinic-table-cell">{record.age}</td>
                </tr>
              ))}
              {!loading && records.length === 0 && (
                <tr><td className="p-4" colSpan={4}>No vitals recorded for this patient yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}



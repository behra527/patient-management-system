"use client";

import { useState, type FormEvent } from "react";
import type { Invoice, PaymentMethod, PaymentPayload } from "@/lib/api";

type PaymentFormProps = {
  invoice: Invoice | null;
  saving: boolean;
  error: string;
  onSubmit: (
    invoiceId: number,
    payload: PaymentPayload,
  ) => Promise<void>;
  onCancel: () => void;
};

const paymentMethods: PaymentMethod[] = [
  "Cash",
  "Card",
  "Bank Transfer",
  "Online",
];

function formatPkr(amountPaisa: number): string {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 2,
  }).format(amountPaisa / 100);
}

export default function PaymentForm({
  invoice,
  saving,
  error,
  onSubmit,
  onCancel,
}: PaymentFormProps) {
  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState<PaymentMethod>("Cash");
  const [reference, setReference] = useState("");

  if (!invoice) {
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!invoice) return;

    const amountPaisa = Math.round(Number(amount) * 100);

    if (
      !Number.isSafeInteger(amountPaisa) ||
      amountPaisa <= 0 ||
      amountPaisa > invoice.balance_due_paisa
    ) {
      return;
    }

    await onSubmit(invoice.id, {
      amount_paisa: amountPaisa,
      payment_method: method,
      reference: reference.trim() || null,
    });

    setAmount("");
    setMethod("Cash");
    setReference("");
  }

  return (
    <section className="payment-form-section">
      <div className="section-heading">
        <div>
          <h2>Record Payment</h2>
          <p>
            Invoice {invoice.invoice_number} — Balance due:{" "}
            {formatPkr(invoice.balance_due_paisa)}
          </p>
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
            Payment Amount (PKR)
            <input
              type="number"
              min="0.01"
              max={(invoice.balance_due_paisa / 100).toFixed(2)}
              step="0.01"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
              placeholder="Enter payment amount"
            />
          </label>

          <label>
            Payment Method
            <select
              value={method}
              onChange={(event) =>
                setMethod(event.target.value as PaymentMethod)
              }
              required
            >
              {paymentMethods.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="form-full-width">
            Reference (Optional)
            <input
              value={reference}
              onChange={(event) => setReference(event.target.value)}
              maxLength={100}
              placeholder="Transaction ID or receipt reference"
            />
          </label>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onCancel} disabled={saving}>
            Cancel
          </button>
          <button type="submit" disabled={saving || invoice.balance_due_paisa <= 0}>
            {saving ? "Recording Payment..." : "Record Payment"}
          </button>
        </div>
      </form>
    </section>
  );
}

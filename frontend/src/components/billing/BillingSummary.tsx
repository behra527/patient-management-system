"use client";

import { useMemo } from "react";
import type { Invoice } from "@/lib/api";

type BillingSummaryProps = {
  invoices: Invoice[];
  loading: boolean;
};

function formatPkr(amountPaisa: number): string {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 2,
  }).format(amountPaisa / 100);
}

export default function BillingSummary({
  invoices,
  loading,
}: BillingSummaryProps) {
  const summary = useMemo(
    () =>
      invoices.reduce(
        (totals, invoice) => ({
          billed: totals.billed + invoice.total_amount_paisa,
          received: totals.received + invoice.amount_paid_paisa,
          outstanding: totals.outstanding + invoice.balance_due_paisa,
        }),
        { billed: 0, received: 0, outstanding: 0 },
      ),
    [invoices],
  );

  const metrics = [
    {
      label: "Total Billed",
      amount: summary.billed,
      description: "Total invoice value",
    },
    {
      label: "Payments Received",
      amount: summary.received,
      description: "Amount collected",
    },
    {
      label: "Outstanding Balance",
      amount: summary.outstanding,
      description: "Amount remaining",
    },
  ];

  return (
    <section className="billing-summary-section">
      <div className="section-heading">
        <div>
          <h2>Billing Overview</h2>
          <p>Financial summary of the currently loaded invoices.</p>
        </div>
      </div>

      <div className="billing-summary-grid">
        {metrics.map((metric) => (
          <article className="billing-summary-card" key={metric.label}>
            <p>{metric.label}</p>
            <h3>
              {loading ? "Loading..." : formatPkr(metric.amount)}
            </h3>
            <span>{metric.description}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

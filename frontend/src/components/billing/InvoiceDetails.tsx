"use client";

import type { InvoiceDetail } from "@/lib/api";

type InvoiceDetailsProps = {
  invoice: InvoiceDetail | null;
  loading: boolean;
  error: string;
  onClose: () => void;
  onRecordPayment: () => void;
};

function formatPkr(amountPaisa: number): string {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 2,
  }).format(amountPaisa / 100);
}

function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString("en-PK", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function InvoiceDetails({
  invoice,
  loading,
  error,
  onClose,
  onRecordPayment,
}: InvoiceDetailsProps) {
  if (!invoice && !loading && !error) return null;

  const status = invoice?.status?.toLowerCase() ?? "";
  const isPaid = status === "paid";
  const isOverdue = status === "overdue";

  const statusStyle = isPaid
    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
    : isOverdue
      ? "border-red-200 bg-red-50 text-red-700"
      : "border-amber-200 bg-amber-50 text-amber-700";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-950/50 p-3 backdrop-blur-sm sm:p-6"
      onClick={onClose}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="invoice-details-heading"
        className="my-auto w-full max-w-2xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="flex items-start justify-between gap-4 border-b border-slate-200 bg-slate-50 px-4 py-3 sm:px-5">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
              <svg
                aria-hidden="true"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
                className="h-6 w-6"
              >
                <path d="M7 3.75h7l4 4V20a.75.75 0 0 1-.75.75h-10.5A.75.75 0 0 1 6 20V4.5a.75.75 0 0 1 .75-.75Z" />
                <path d="M14 4v4h4M9 13h6M9 16.5h6" />
              </svg>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">
                Billing &amp; Finance
              </p>
              <h2
                id="invoice-details-heading"
                className="mt-1 text-lg font-bold tracking-tight text-slate-900 sm:text-2xl"
              >
                Invoice Details
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Invoice information and payment history
              </p>
              {invoice && (
                <p className="mt-2 text-sm font-semibold text-slate-700">
                  {invoice.invoice_number}
                </p>
              )}
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close invoice details"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="h-5 w-5"
            >
              <path d="m18 6-12 12M6 6l12 12" />
            </svg>
          </button>
        </header>

        <div className="max-h-[75vh] overflow-y-auto px-4 py-3 sm:px-5">
          {loading && (
            <div role="status" className="py-12 text-center">
              <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
              <p className="mt-4 text-sm font-medium text-slate-600">
                Loading invoice details...
              </p>
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              <p className="font-semibold">Unable to load invoice</p>
              <p className="mt-1">{error}</p>
            </div>
          )}

          {invoice && !loading && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-slate-500">Invoice status</p>
                  <span
                    className={`mt-2 inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-bold ${statusStyle}`}
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-current" />
                    {invoice.status}
                  </span>
                </div>

                {invoice.balance_due_paisa > 0 && (
                  <button
                    type="button"
                    onClick={onRecordPayment}
                    className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    + Record Payment
                  </button>
                )}
              </div>

              <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
                  <p className="text-sm font-medium text-slate-500">
                    Total Amount
                  </p>
                  <p className="mt-1.5 text-base font-bold tracking-tight text-slate-900">
                    {formatPkr(invoice.total_amount_paisa)}
                  </p>
                  <p className="mt-2 text-xs text-slate-400">
                    Total invoice value
                  </p>
                </div>

                <div className="rounded-xl border border-emerald-200 bg-emerald-50/60 p-3 shadow-sm">
                  <p className="text-sm font-medium text-emerald-800">
                    Paid Amount
                  </p>
                  <p className="mt-1.5 text-base font-bold tracking-tight text-emerald-700">
                    {formatPkr(invoice.amount_paid_paisa)}
                  </p>
                  <p className="mt-2 text-xs text-emerald-700/70">
                    Payments received
                  </p>
                </div>

                <div className="rounded-xl border border-amber-200 bg-amber-50/60 p-3 shadow-sm">
                  <p className="text-sm font-medium text-amber-800">
                    Balance Due
                  </p>
                  <p className="mt-1.5 text-base font-bold tracking-tight text-amber-700">
                    {formatPkr(invoice.balance_due_paisa)}
                  </p>
                  <p className="mt-2 text-xs text-amber-700/70">
                    Remaining amount
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Invoice Information
                </h3>
                <div className="mt-3 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-slate-200 bg-slate-200 sm:grid-cols-2">
                  <div className="bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Invoice Number
                    </p>
                    <p className="mt-2 break-words text-sm font-semibold text-slate-900">
                      {invoice.invoice_number}
                    </p>
                  </div>

                  <div className="bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Patient ID
                    </p>
                    <p className="mt-1.5 text-sm font-semibold text-slate-900">
                      {invoice.patient_id}
                    </p>
                  </div>

                  <div className="bg-white p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Description
                    </p>
                    <p className="mt-2 break-words text-sm text-slate-800">
                      {invoice.description}
                    </p>
                  </div>

                  <div className="bg-white p-4">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Due Date
                    </p>
                    <p className="mt-1.5 text-sm font-semibold text-slate-900">
                      {formatDate(invoice.due_date)}
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex flex-wrap items-end justify-between gap-3">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">
                      Payment History
                    </h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Recorded transactions for this invoice
                    </p>
                  </div>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                    {invoice.payments.length}{" "}
                    {invoice.payments.length === 1 ? "payment" : "payments"}
                  </span>
                </div>

                {invoice.payments.length === 0 ? (
                  <div className="mt-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-10 text-center">
                    <p className="text-sm font-semibold text-slate-700">
                      No payments recorded
                    </p>
                    <p className="mt-1 text-sm text-slate-500">
                      Payment transactions will appear here once recorded.
                    </p>
                  </div>
                ) : (
                  <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200">
                    <table className="w-full min-w-[600px] divide-y divide-slate-200 text-left">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-slate-500">
                            Date
                          </th>
                          <th className="px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-slate-500">
                            Amount
                          </th>
                          <th className="px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-slate-500">
                            Method
                          </th>
                          <th className="px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-slate-500">
                            Reference
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 bg-white">
                        {invoice.payments.map((payment) => (
                          <tr
                            key={payment.id}
                            className="transition hover:bg-slate-50"
                          >
                            <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                              {formatDate(payment.paid_at)}
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-sm font-semibold tabular-nums text-slate-900">
                              {formatPkr(payment.amount_paisa)}
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-700">
                              {payment.payment_method}
                            </td>
                            <td className="px-4 py-3 text-sm text-slate-500">
                              {payment.reference || "—"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <footer className="flex justify-end border-t border-slate-200 bg-slate-50 px-5 py-3 sm:px-6">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Close Details
          </button>
        </footer>
      </section>
    </div>
  );
}



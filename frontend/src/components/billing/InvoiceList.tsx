"use client";

import { useEffect, useMemo, useState } from "react";
import type { Invoice, InvoiceStatus, Patient } from "@/lib/api";

type InvoiceListProps = {
  invoices: Invoice[];
  patients: Patient[];
  loading: boolean;
  status: InvoiceStatus | "";
  onStatusChange: (status: InvoiceStatus | "") => void;
  onSelectInvoice: (invoice: Invoice) => void;
};

const invoiceStatuses: Array<InvoiceStatus | ""> = [
  "",
  "Unpaid",
  "Partially Paid",
  "Paid",
];

const PAGE_SIZE = 5;

function formatPkr(amountPaisa: number): string {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 2,
  }).format(amountPaisa / 100);
}

export default function InvoiceList({
  invoices,
  patients,
  loading,
  status,
  onStatusChange,
  onSelectInvoice,
}: InvoiceListProps) {
  const [currentPage, setCurrentPage] = useState(1);

  const patientNames = useMemo(
    () => new Map(patients.map((patient) => [patient.id, patient.full_name])),
    [patients],
  );

  const totalPages = Math.max(1, Math.ceil(invoices.length / PAGE_SIZE));
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const visibleInvoices = invoices.slice(startIndex, startIndex + PAGE_SIZE);

  useEffect(() => {
    setCurrentPage(1);
  }, [status]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  const firstItem = invoices.length === 0 ? 0 : startIndex + 1;
  const lastItem = Math.min(startIndex + PAGE_SIZE, invoices.length);

  return (
    <section className="billing-list-section overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-4 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Invoices</h2>
          <p className="mt-1 text-sm text-slate-500">
            Review invoices and outstanding balances.
          </p>
        </div>

        <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-600 sm:min-w-44">
          Filter by status
          <select
            className="rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            value={status}
            onChange={(event) =>
              onStatusChange(event.target.value as InvoiceStatus | "")
            }
          >
            {invoiceStatuses.map((item) => (
              <option key={item || "All"} value={item}>
                {item || "All statuses"}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading ? (
        <p role="status" className="px-5 py-10 text-center text-sm text-slate-500">
          Loading invoices...
        </p>
      ) : invoices.length === 0 ? (
        <p className="px-5 py-10 text-center text-sm text-slate-500">
          No invoices found for this filter.
        </p>
      ) : (
        <>
          <div className="table-responsive overflow-x-auto">
            <table className="billing-table w-full min-w-[900px] text-left">
              <thead className="bg-slate-50">
                <tr>
                  {[
                    "Invoice",
                    "Patient",
                    "Total",
                    "Paid",
                    "Balance Due",
                    "Due Date",
                    "Status",
                    "Details",
                  ].map((heading) => (
                    <th
                      key={heading}
                      className="whitespace-nowrap border-b border-slate-200 px-4 py-3 text-xs font-bold uppercase tracking-wide text-slate-500"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {visibleInvoices.map((invoice) => (
                  <tr
                    key={invoice.id}
                    className="transition-colors hover:bg-slate-50"
                  >
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-semibold text-slate-800">
                      {invoice.invoice_number}
                    </td>
                    <td className="max-w-44 truncate px-4 py-3 text-sm text-slate-600">
                      {patientNames.get(invoice.patient_id) ??
                        `Patient #${invoice.patient_id}`}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-700">
                      {formatPkr(invoice.total_amount_paisa)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-700">
                      {formatPkr(invoice.amount_paid_paisa)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-semibold text-slate-800">
                      {formatPkr(invoice.balance_due_paisa)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-slate-600">
                      {invoice.due_date}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <span
                        className={`invoice-status invoice-status-${invoice.status
                          .toLowerCase()
                          .replaceAll(" ", "-")} inline-flex rounded-full px-2.5 py-1 text-xs font-semibold`}
                      >
                        {invoice.status}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <button
                        type="button"
                        onClick={() => onSelectInvoice(invoice)}
                        className="rounded-md px-2 py-1.5 text-sm font-semibold text-blue-700 transition hover:bg-blue-50 hover:text-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        View details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-3 border-t border-slate-200 bg-white px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-slate-500">
              Showing{" "}
              <span className="font-semibold text-slate-800">{firstItem}</span>
              {" "}–{" "}
              <span className="font-semibold text-slate-800">{lastItem}</span>
              {" "}of{" "}
              <span className="font-semibold text-slate-800">{invoices.length}</span>
              {" "}invoices
            </p>

            <div className="flex flex-wrap items-center gap-1.5">
              <button
                type="button"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>

              {Array.from({ length: totalPages }, (_, index) => index + 1).map(
                (page) => (
                  <button
                    key={page}
                    type="button"
                    aria-current={currentPage === page ? "page" : undefined}
                    onClick={() => setCurrentPage(page)}
                    className={`h-9 min-w-9 rounded-lg border px-3 text-sm font-semibold transition ${
                      currentPage === page
                        ? "border-blue-600 bg-blue-600 text-white"
                        : "border-slate-300 text-slate-700 hover:bg-slate-50"
                    }`}
                  >
                    {page}
                  </button>
                ),
              )}

              <button
                type="button"
                disabled={currentPage === totalPages}
                onClick={() =>
                  setCurrentPage((page) => Math.min(totalPages, page + 1))
                }
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

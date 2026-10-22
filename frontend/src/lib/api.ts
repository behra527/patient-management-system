
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const TOKEN_KEY = "clinic_access_token";

export type Gender = "Male" | "Female" | "Other";

export type Patient = {
  id: number;
  full_name: string;
  date_of_birth: string;
  gender: Gender;
  phone: string | null;
  email: string | null;
  address: string | null;
  created_at: string;
  updated_at: string;
};

export type PatientPayload = {
  full_name: string;
  date_of_birth: string;
  gender: Gender;
  phone: string | null;
  email: string | null;
  address: string | null;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function clearAccessToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function hasAccessToken(): boolean {
  return Boolean(getAccessToken());
}

function getErrorMessage(
  body: unknown,
  statusCode: number,
): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail?: unknown }).detail;

    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail.map((item: unknown) => {
        if (
          item &&
          typeof item === "object" &&
          "msg" in item &&
          typeof item.msg === "string"
        ) {
          return item.msg;
        }

        return "Invalid data";
      });

      if (messages.length > 0) {
        return messages.join(", ");
      }
    }
  }

  switch (statusCode) {
    case 400:
      return "The request could not be processed.";
    case 401:
      return "Your session is invalid or has expired. Please log in again.";
    case 403:
      return "You do not have permission to perform this action.";
    case 404:
      return "The requested record was not found.";
    case 409:
      return "This operation conflicts with an existing record.";
    case 422:
      return "Please check the submitted information.";
    case 429:
      return "Too many requests. Please try again shortly.";
    default:
      return `Request failed with status ${statusCode}.`;
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  includeAuth = true,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (
    options.body !== undefined &&
    options.body !== null &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  headers.set("Accept", "application/json");

  if (includeAuth) {
    const token = getAccessToken();

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error(
      "Unable to connect to the API. Check that the FastAPI server is running.",
    );
  }

  if (!response.ok) {
    let body: unknown = null;

    try {
      body = await response.json();
    } catch {
      // Some server errors may not contain a JSON response.
    }

    if (response.status === 401 && includeAuth) {
      clearAccessToken();
    }

    throw new Error(getErrorMessage(body, response.status));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (response.status === 205) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") ?? "";

  if (!contentType.toLowerCase().includes("application/json")) {
    throw new Error(
      "The API returned an unexpected response format.",
    );
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new Error("The API returned invalid JSON.");
  }
}

export async function login(
  username: string,
  password: string,
): Promise<LoginResponse> {
  const result = await request<LoginResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ username, password }),
    },
    false,
  );

  if (!result.access_token) {
    throw new Error("The login response did not contain an access token.");
  }

  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, result.access_token);
  }

  return result;
}

export function getPatients(): Promise<Patient[]> {
  return request<Patient[]>("/patients/");
}

export function createPatient(
  payload: PatientPayload,
): Promise<Patient> {
  return request<Patient>("/patients/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updatePatient(
  patientId: number,
  payload: PatientPayload,
): Promise<Patient> {
  return request<Patient>(`/patients/${patientId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deletePatient(
  patientId: number,
): Promise<void> {
  return request<void>(`/patients/${patientId}`, {
    method: "DELETE",
  });
}

// Appointment API
export type AppointmentStatus = "Scheduled" | "Completed" | "Cancelled";

export type Appointment = {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  appointment_time: string;
  duration_minutes: number;
  reason: string;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
};

export type AppointmentPayload = {
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  appointment_time: string;
  duration_minutes: number;
  reason: string;
};

export type DoctorStatus = "Active" | "Inactive" | "On Leave";

export type Doctor = {
  id: number;
  full_name: string;
  specialty: string;
  email: string;
  phone: string | null;
  license_number: string;
  status: DoctorStatus;
  created_at: string;
  updated_at: string;
};

export type DoctorPayload = {
  full_name: string;
  specialty: string;
  email: string;
  phone: string | null;
  license_number: string;
  status: DoctorStatus;
};

export function getAppointments(
  filters: { status?: AppointmentStatus } = {},
): Promise<Appointment[]> {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  const query = params.toString();
  return request<Appointment[]>(`/appointments/${query ? `?${query}` : ""}`);
}

export function createAppointment(
  payload: AppointmentPayload,
): Promise<Appointment> {
  return request<Appointment>("/appointments/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAppointmentStatus(
  appointmentId: number,
  status: AppointmentStatus,
): Promise<Appointment> {
  return request<Appointment>(`/appointments/${appointmentId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function getDoctors(): Promise<Doctor[]> {
  return request<Doctor[]>("/doctors/");
}

// Billing API
export type InvoiceStatus = "Unpaid" | "Partially Paid" | "Paid";

export type PaymentMethod =
  | "Cash"
  | "Card"
  | "Bank Transfer"
  | "Online";

export type Invoice = {
  id: number;
  invoice_number: string;
  patient_id: number;
  appointment_id: number | null;
  description: string;
  total_amount_paisa: number;
  amount_paid_paisa: number;
  balance_due_paisa: number;
  due_date: string;
  status: InvoiceStatus;
  created_at: string;
  updated_at: string;
};

export type Payment = {
  id: number;
  invoice_id: number;
  amount_paisa: number;
  payment_method: PaymentMethod;
  reference: string | null;
  paid_at: string;
};

export type InvoiceDetail = Invoice & {
  payments: Payment[];
};

export type InvoicePayload = {
  invoice_number: string;
  patient_id: number;
  appointment_id: number | null;
  description: string;
  total_amount_paisa: number;
  due_date: string;
};

export type PaymentPayload = {
  amount_paisa: number;
  payment_method: PaymentMethod;
  reference: string | null;
};

export function getInvoices(
  filters: { patient_id?: number; status?: InvoiceStatus } = {},
): Promise<Invoice[]> {
  const params = new URLSearchParams();

  if (filters.patient_id) {
    params.set("patient_id", String(filters.patient_id));
  }

  if (filters.status) {
    params.set("status", filters.status);
  }

  const query = params.toString();

  return request<Invoice[]>(
    `/billing/invoices${query ? `?${query}` : ""}`,
  );
}

export function createInvoice(
  payload: InvoicePayload,
): Promise<Invoice> {
  return request<Invoice>("/billing/invoices", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getInvoiceDetails(
  invoiceId: number,
): Promise<InvoiceDetail> {
  return request<InvoiceDetail>(`/billing/invoices/${invoiceId}`);
}

export function recordInvoicePayment(
  invoiceId: number,
  payload: PaymentPayload,
): Promise<Payment> {
  return request<Payment>(`/billing/invoices/${invoiceId}/payments`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// Doctor management API
export function createDoctor(payload: DoctorPayload): Promise<Doctor> {
  return request<Doctor>("/doctors/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateDoctor(
  doctorId: number,
  payload: DoctorPayload,
): Promise<Doctor> {
  return request<Doctor>(`/doctors/${doctorId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deactivateDoctor(doctorId: number): Promise<Doctor> {
  return request<Doctor>(`/doctors/${doctorId}/deactivate`, {
    method: "PATCH",
  });
}

// Vitals / health metrics API
export type VitalsPayload = {
  patient_id: string;
  age: number;
  blood_pressure: {
    systolic: number;
    diastolic: number;
  };
  glucose_level: number;
};

export type VitalsRecord = VitalsPayload & {
  id: number;
  recorded_at: string;
};

export type VitalsSummary = {
  patient_id: string;
  average_systolic: number;
  average_diastolic: number;
  average_glucose_level: number;
  total_records: number;
};

export function createVitals(payload: VitalsPayload): Promise<VitalsRecord> {
  return request<VitalsRecord>("/vitals", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getPatientVitals(
  patientId: string,
): Promise<VitalsRecord[]> {
  return request<VitalsRecord[]>(
    `/patients/${encodeURIComponent(patientId)}/vitals`,
  );
}

export function getPatientVitalsSummary(
  patientId: string,
): Promise<VitalsSummary> {
  return request<VitalsSummary>(
    `/patients/${encodeURIComponent(patientId)}/summary`,
  );
}



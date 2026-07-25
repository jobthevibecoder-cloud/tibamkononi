import { getSession } from "./session";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://tibamkononi.onrender.com";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function authHeaders(): HeadersInit {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  const session = getSession();
  if (session?.token) {
    headers["Authorization"] = `Bearer ${session.token}`;
  }
  return headers;
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    let message = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      if (Array.isArray(body?.detail)) {
        message = body.detail
          .map((d: any) => {
            const field = Array.isArray(d?.loc) ? d.loc.filter((p: any) => p !== "body").join(".") : "field";
            return `${field}: ${d?.msg ?? "invalid value"}`;
          })
          .join("; ");
      } else if (typeof body?.detail === "string") {
        message = body.detail;
      }
    } catch {
      // response body wasn't JSON, keep the default message
    }
    throw new ApiError(message, res.status);
  }
  return res.json();
}

export async function apiGet(endpoint: string) {
  const res = await fetch(`${API_BASE}${endpoint}`, { cache: "no-store", headers: authHeaders() });
  return handleResponse(res);
}

export async function apiPost(endpoint: string, data: unknown) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

export { API_BASE };

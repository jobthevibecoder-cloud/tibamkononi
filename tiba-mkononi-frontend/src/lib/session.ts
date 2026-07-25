export type Session = {
  token?: string;
  role?: string;
  name?: string;
  hospital_slug?: string;
  hospital_name?: string;
  county_code?: string;
};

const KEY = "tiba_session";

export function saveSession(session: Session) {
  if (typeof window !== "undefined") {
    sessionStorage.setItem(KEY, JSON.stringify(session));
  }
}

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Session;
  } catch {
    return null;
  }
}

export function clearSession() {
  if (typeof window !== "undefined") sessionStorage.removeItem(KEY);
}

export function formatRole(role?: string) {
  if (!role) return "";
  return role
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

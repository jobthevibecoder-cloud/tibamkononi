"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, LogIn, TriangleAlert } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { saveSession } from "@/lib/session";

type HospitalOption = { slug: string; name: string };

function roleRoute(role: string, slug: string) {
  const r = (role || "").toUpperCase();
  if (r.includes("DOCTOR")) return `/dashboard/${slug}/medical`;
  if (r.includes("NURSE")) return `/dashboard/${slug}/patient-care`;
  return `/dashboard/${slug}/hospital-staff`;
}

export default function LoginPage() {
  const router = useRouter();
  const [hospitals, setHospitals] = useState<HospitalOption[]>([]);
  const [hospitalSlug, setHospitalSlug] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet("/v1/hospitals/")
      .then((data) => setHospitals(Array.isArray(data) ? data : data?.hospitals ?? []))
      .catch(() => setHospitals([]));
  }, []);

  async function handleLogin() {
    if (!hospitalSlug || !email || !password) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost("/v1/auth/login", { email, password });
      const role = data?.user?.role ?? "PHARMACIST";
      const name = data?.user?.full_name ?? email;
      const hospitalName = hospitals.find((h) => h.slug === hospitalSlug)?.name;
      saveSession({
        token: data?.access_token,
        role,
        name,
        hospital_slug: hospitalSlug,
        hospital_name: hospitalName,
      });
      router.push(roleRoute(role, hospitalSlug));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed. Check your credentials and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="clay-card space-y-5 p-8">
        <div className="text-center">
          <h1 className="text-xl font-bold text-stone-900">Hospital Staff Login</h1>
          <p className="mt-1 text-sm text-stone-500">Sign in to manage your hospital&apos;s dashboard.</p>
        </div>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-stone-600">Hospital</span>
          <select className="clay-input w-full px-4 py-2.5" value={hospitalSlug} onChange={(e) => setHospitalSlug(e.target.value)}>
            <option value="">Select your hospital</option>
            {hospitals.map((h) => (
              <option key={h.slug} value={h.slug}>{h.name}</option>
            ))}
          </select>
          <span className="block text-xs text-stone-400">Used to route you to the right dashboard - the login itself does not send this yet.</span>
        </label>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-stone-600">Email</span>
          <input type="email" className="clay-input w-full px-4 py-2.5" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-stone-600">Password</span>
          <input type="password" className="clay-input w-full px-4 py-2.5" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>

        {error && (
          <div className="flex items-center gap-2 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">
            <TriangleAlert size={16} /> {error}
          </div>
        )}

        <button
          onClick={handleLogin}
          disabled={loading || !hospitalSlug || !email || !password}
          className="clay-btn flex w-full items-center justify-center gap-2 rounded-2xl px-6 py-3 font-semibold"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <LogIn size={18} />}
          {loading ? "Logging in..." : "Login"}
        </button>

        <p className="text-center text-xs text-stone-400">
          Don&apos;t have an account? Contact your hospital director.
        </p>
      </div>
    </div>
  );
}

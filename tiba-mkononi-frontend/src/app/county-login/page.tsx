"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, ShieldCheck, TriangleAlert } from "lucide-react";
import { apiPost } from "@/lib/api";
import { saveSession } from "@/lib/session";

export default function CountyLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogin() {
    if (!email || !password) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost("/v1/auth/login", { email, password });
      const role = (data?.user?.role ?? "").toUpperCase();
      if (!role.includes("COUNTY")) {
        setError("This login is for County Directors only. Hospital staff should use the staff login.");
        return;
      }
      saveSession({
        token: data?.access_token,
        role,
        name: data?.user?.full_name ?? email,
      });
      router.push("/county");
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
          <div className="clay-card-flat mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-2xl text-amber-900">
            <ShieldCheck size={22} />
          </div>
          <h1 className="text-xl font-bold text-stone-900">County Director Login</h1>
        </div>

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
          disabled={loading || !email || !password}
          className="clay-btn flex w-full items-center justify-center gap-2 rounded-2xl px-6 py-3 font-semibold"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <ShieldCheck size={18} />}
          {loading ? "Logging in..." : "Login"}
        </button>
      </div>
    </div>
  );
}

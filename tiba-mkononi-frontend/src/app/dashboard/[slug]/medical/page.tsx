"use client";

import { useEffect, useState } from "react";
import { Loader2, LogOut } from "lucide-react";
import { apiGet } from "@/lib/api";
import { getSession, clearSession, formatRole } from "@/lib/session";
import type { Session } from "@/lib/session";

type Patient = { id?: string; full_name: string; age?: number; gender?: string; status?: string };

function timeForIndex(i: number) {
  const totalMinutes = 8 * 60 + i * 30;
  const h = Math.floor(totalMinutes / 60);
  const m = totalMinutes % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export default function MedicalDashboard({ params }: { params: { slug: string } }) {
  const { slug } = params;
  const [session, setSession] = useState<Session | null>(null);
  const [queue, setQueue] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setSession(getSession());
    apiGet(`/v1/hospitals/${slug}/patients`)
      .then((data) => setQueue(Array.isArray(data) ? data : data?.patients ?? []))
      .catch(() => setQueue([]))
      .finally(() => setLoading(false));
  }, [slug]);

  const statusColor: Record<string, string> = {
    done: "text-green-600",
    waiting: "text-amber-600",
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-stone-900">{session?.hospital_name ?? slug}</h1>
          <p className="text-sm text-stone-500">{session?.name ?? "Doctor"}{session?.role ? ` - ${formatRole(session.role)}` : ""} - Medical Staff Section</p>
        </div>
        <button onClick={() => clearSession()} className="clay-btn-secondary flex items-center gap-1 rounded-xl px-3 py-2 text-sm">
          <LogOut size={14} /> Log out
        </button>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={16} className="animate-spin" /> Loading queue...</div>
      ) : (
        <div className="clay-card p-6">
          <h2 className="mb-4 font-bold text-stone-900">Today's Patient Queue - {queue.length} patients</h2>
          {queue.length === 0 ? (
            <p className="text-sm text-stone-500">No patients queued yet.</p>
          ) : (
            <div className="divide-y divide-stone-200">
              {queue.map((p, i) => (
                <div key={p.id ?? i} className="flex flex-wrap items-center justify-between gap-2 py-2.5 text-sm">
                  <span className="w-16 font-medium text-stone-800">{timeForIndex(i)}</span>
                  <span className="flex-1 text-stone-700">{p.full_name}</span>
                  <span className="flex-1 text-stone-500">
                    {p.age !== undefined ? `${p.age} yrs` : ""}{p.age !== undefined && p.gender ? ", " : ""}{p.gender ?? ""}
                  </span>
                  <span className={`text-xs font-bold ${statusColor[(p.status ?? "").toLowerCase()] ?? "text-stone-400"}`}>
                    {p.status ?? "-"}
                  </span>
                </div>
              ))}
            </div>
          )}
          <p className="mt-3 text-xs text-stone-400">Times shown above are generated on the frontend - the backend doesn't return appointment times yet.</p>
        </div>
      )}

      <div className="space-y-1 text-sm text-stone-400">
        <p>Hospital Staff - Locked (Pharmacy/Admin Only)</p>
        <p>Patient Care - Locked (Nurses Only)</p>
      </div>
    </div>
  );
}

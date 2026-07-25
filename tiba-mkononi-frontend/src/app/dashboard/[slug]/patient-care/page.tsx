"use client";

import { useEffect, useState } from "react";
import { Loader2, LogOut } from "lucide-react";
import { apiGet } from "@/lib/api";
import { getSession, clearSession, formatRole } from "@/lib/session";
import type { Session } from "@/lib/session";

type Ward = { name: string; type?: string; total_beds: number; occupied_beds: number };

export default function PatientCareDashboard({ params }: { params: { slug: string } }) {
  const { slug } = params;
  const [session, setSession] = useState<Session | null>(null);
  const [wards, setWards] = useState<Ward[]>([]);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState("");

  useEffect(() => {
    setSession(getSession());
    apiGet(`/v1/hospitals/${slug}/beds`)
      .then((data) => setWards(Array.isArray(data) ? data : data?.wards ?? []))
      .catch(() => setWards([]))
      .finally(() => setLoading(false));
  }, [slug]);

  function statusFor(pct: number) {
    if (pct >= 100) return { label: "FULL", color: "text-red-600" };
    if (pct >= 85) return { label: "Near Full", color: "text-amber-600" };
    if (pct >= 60) return { label: "Filling Up", color: "text-yellow-600" };
    return { label: "Available", color: "text-green-600" };
  }

  function showStub(message: string) {
    setNote(message);
    setTimeout(() => setNote(""), 3000);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-stone-900">{session?.hospital_name ?? slug}</h1>
          <p className="text-sm text-stone-500">{session?.name ?? "Nurse"}{session?.role ? ` - ${formatRole(session.role)}` : ""} - Patient Care Section</p>
        </div>
        <button onClick={() => clearSession()} className="clay-btn-secondary flex items-center gap-1 rounded-xl px-3 py-2 text-sm">
          <LogOut size={14} /> Log out
        </button>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={16} className="animate-spin" /> Loading beds...</div>
      ) : (
        <div className="clay-card space-y-3 p-6">
          <h2 className="font-bold text-stone-900">Bed Management</h2>
          {wards.length === 0 ? (
            <p className="text-sm text-stone-500">No ward data yet.</p>
          ) : (
            <div className="divide-y divide-stone-200">
              {wards.map((w, i) => {
                const pct = w.total_beds > 0 ? (w.occupied_beds / w.total_beds) * 100 : 0;
                const s = statusFor(pct);
                return (
                  <div key={i} className="flex flex-wrap items-center justify-between gap-2 py-2.5 text-sm">
                    <span className="w-36 font-medium text-stone-800">{w.name}</span>
                    <span className="text-stone-500">{w.occupied_beds}/{w.total_beds}</span>
                    <span className="text-stone-500">{Math.max(w.total_beds - w.occupied_beds, 0)} free</span>
                    <span className={`font-bold ${s.color}`}>{s.label}</span>
                  </div>
                );
              })}
            </div>
          )}

          <div className="flex flex-wrap gap-2 pt-2">
            <button onClick={() => showStub("Admit flow isn't wired up yet - connect a beds-update endpoint.")} className="clay-btn rounded-xl px-4 py-2 text-sm">Admit Patient</button>
            <button onClick={() => showStub("Transfer flow isn't wired up yet.")} className="clay-btn-secondary rounded-xl px-4 py-2 text-sm">Transfer</button>
            <button onClick={() => showStub("Discharge flow isn't wired up yet.")} className="clay-btn-secondary rounded-xl px-4 py-2 text-sm">Discharge</button>
          </div>
          {note && <p className="text-xs text-stone-500">{note}</p>}
        </div>
      )}

      <div className="space-y-1 text-sm text-stone-400">
        <p>Medical Staff - Locked (Doctors Only)</p>
        <p>Hospital Staff - Locked (Pharmacy/Admin Only)</p>
      </div>
    </div>
  );
}

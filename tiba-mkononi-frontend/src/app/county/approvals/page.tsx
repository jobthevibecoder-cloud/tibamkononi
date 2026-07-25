"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, ArrowLeft, CircleCheck, CircleX, ShieldCheck, MessageSquare } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";

type PendingApproval = {
  id: string;
  name: string;
  license_number?: string;
  type?: string;
  location?: string;
  director?: string;
  submitted_at?: string;
  buildings_count?: number;
  beds_total?: number;
  amenities?: string[];
  staff_count?: number;
};

export default function ApprovalsPage() {
  const [pending, setPending] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [actioning, setActioning] = useState<string | null>(null);
  const [approved, setApproved] = useState<Record<string, boolean>>({});
  const [noteShown, setNoteShown] = useState<Record<string, string>>({});
  const [showReject, setShowReject] = useState<Record<string, boolean>>({});
  const [reasonDraft, setReasonDraft] = useState<Record<string, string>>({});

  useEffect(() => {
    apiGet("/v1/county/approvals")
      .then((data) => setPending(data?.pending ?? (Array.isArray(data) ? data : [])))
      .catch(() => setPending([]))
      .finally(() => setLoading(false));
  }, []);

  async function approveHospital(id: string) {
    setActioning(id);
    try {
      await apiPost(`/v1/county/approvals/${id}/approve`, {});
      setApproved((a) => ({ ...a, [id]: true }));
    } catch (e) {
      setNoteShown((n) => ({ ...n, [id]: e instanceof Error ? e.message : "Action failed." }));
    } finally {
      setActioning(null);
    }
  }

  async function rejectHospital(id: string) {
    const reason = reasonDraft[id] ?? "";
    setActioning(id);
    try {
      await apiPost(`/v1/county/approvals/${id}/reject?reason=${encodeURIComponent(reason)}`, {});
      setPending((p) => p.filter((h) => h.id !== id));
    } catch (e) {
      setNoteShown((n) => ({ ...n, [id]: e instanceof Error ? e.message : "Action failed." }));
    } finally {
      setActioning(null);
      setShowReject((s) => ({ ...s, [id]: false }));
    }
  }

  function showStub(id: string, message: string) {
    setNoteShown((n) => ({ ...n, [id]: message }));
    setTimeout(() => setNoteShown((n) => ({ ...n, [id]: "" })), 4000);
  }

  const visible = pending.filter((h) => !approved[h.id]);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link href="/county" className="flex items-center gap-1 text-sm font-medium text-stone-500 hover:text-amber-900">
        <ArrowLeft size={14} /> Back to Dashboard
      </Link>

      <h1 className="text-2xl font-bold text-stone-900">Pending Hospital Approvals ({visible.length})</h1>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={16} className="animate-spin" /> Loading...</div>
      ) : visible.length === 0 ? (
        <div className="clay-card p-8 text-center text-sm text-stone-500">No hospitals awaiting approval.</div>
      ) : (
        <div className="space-y-4">
          {visible.map((h) => (
            <div key={h.id} className="clay-card space-y-3 p-6">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <div className="text-lg font-bold text-stone-900">{h.name}</div>
                  {h.type && <div className="text-xs font-medium text-amber-800">{h.type.split("_").join(" ")}</div>}
                </div>
                {h.submitted_at && (
                  <span className="text-xs text-stone-400">Submitted {new Date(h.submitted_at).toLocaleString()}</span>
                )}
              </div>

              <div className="grid gap-1.5 text-sm text-stone-600 sm:grid-cols-2">
                {h.license_number && <div>License: {h.license_number}</div>}
                {h.location && <div>Location: {h.location}</div>}
                {h.director && <div>Director: {h.director}</div>}
                {(h.buildings_count !== undefined || h.beds_total !== undefined) && (
                  <div>Buildings: {h.buildings_count ?? "-"} | Beds: {h.beds_total ?? "-"}</div>
                )}
                {h.amenities && h.amenities.length > 0 && <div className="sm:col-span-2">Amenities: {h.amenities.join(", ")}</div>}
                {h.staff_count !== undefined && <div>Staff Registered: {h.staff_count}</div>}
              </div>

              {noteShown[h.id] && (
                <div className="rounded-xl bg-stone-100 px-3 py-2 text-xs text-stone-600">{noteShown[h.id]}</div>
              )}

              {showReject[h.id] ? (
                <div className="space-y-2 rounded-xl bg-red-50 p-3">
                  <textarea
                    className="clay-input min-h-[70px] w-full resize-none p-3 text-sm"
                    placeholder="Reason for rejection (optional)"
                    value={reasonDraft[h.id] ?? ""}
                    onChange={(e) => setReasonDraft((d) => ({ ...d, [h.id]: e.target.value }))}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => rejectHospital(h.id)}
                      disabled={actioning === h.id}
                      className="clay-btn flex items-center gap-1 rounded-lg bg-red-700 px-3 py-1.5 text-xs"
                    >
                      {actioning === h.id ? <Loader2 size={14} className="animate-spin" /> : <CircleX size={14} />} Confirm Reject
                    </button>
                    <button onClick={() => setShowReject((s) => ({ ...s, [h.id]: false }))} className="clay-btn-secondary rounded-lg px-3 py-1.5 text-xs">
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-wrap gap-2 pt-1">
                  <button
                    onClick={() => showStub(h.id, "License verification isn't wired up yet - check KMPDC manually for now.")}
                    className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs"
                  >
                    <ShieldCheck size={14} /> Verify KMPDC License
                  </button>
                  <button
                    onClick={() => approveHospital(h.id)}
                    disabled={actioning === h.id}
                    className="clay-btn flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs"
                  >
                    {actioning === h.id ? <Loader2 size={14} className="animate-spin" /> : <CircleCheck size={14} />} Approve
                  </button>
                  <button
                    onClick={() => setShowReject((s) => ({ ...s, [h.id]: true }))}
                    className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs"
                  >
                    <CircleX size={14} /> Reject
                  </button>
                  <button
                    onClick={() => showStub(h.id, "Sent a request for more information (demo only - no messaging endpoint yet).")}
                    className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs"
                  >
                    <MessageSquare size={14} /> Request More Info
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {Object.keys(approved).some((id) => approved[id]) && (
        <div className="space-y-3">
          {pending
            .filter((h) => approved[h.id])
            .map((h) => (
              <div key={h.id} className="clay-card space-y-2 p-5">
                <p className="font-semibold text-green-700">{h.name} has been approved!</p>
                <p className="text-sm text-stone-600">The hospital can now log in and access their dashboard.</p>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import {
  Loader2,
  TriangleAlert,
  Search,
  Plus,
  Send,
  LogOut,
  Radio,
  X,
} from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { getSession, clearSession, formatRole } from "@/lib/session";
import type { Session } from "@/lib/session";

type InventoryItem = {
  id?: string;
  name: string;
  generic_name?: string;
  unit?: string;
  current_stock: number;
  minimum_threshold?: number;
  critical_threshold?: number;
  daily_usage_rate?: number;
  days_left?: number;
  status?: string;
  category?: string;
};

type HospitalOption = { slug: string; name: string };

type DistressResult = {
  signal_id?: string;
  hospital?: string;
  medicine?: string;
  urgency?: string;
  ai_recommendation?: string;
  suggested_source?: string;
  nearby_hospitals?: { id?: string; name: string; slug?: string; distance_km?: number }[];
  status?: string;
};

const TABS = ["Inventory", "Suppliers", "Distress", "Staff"] as const;

function statusOf(item: InventoryItem) {
  return (item.status ?? "").toLowerCase();
}

export default function HospitalStaffDashboard({ params }: { params: { slug: string } }) {
  const { slug } = params;
  const [session, setSession] = useState<Session | null>(null);
  const [tab, setTab] = useState<(typeof TABS)[number]>("Inventory");
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [hospitals, setHospitals] = useState<HospitalOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");

  const [showAdd, setShowAdd] = useState(false);
  const [newMed, setNewMed] = useState({ medicine: "", stock: "", used_per_day: "" });

  const [overlayItem, setOverlayItem] = useState<InventoryItem | null>(null);
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");
  const [checking, setChecking] = useState<string[]>([]);
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [result, setResult] = useState<DistressResult | null>(null);
  const [distressSentCount, setDistressSentCount] = useState(0);

  useEffect(() => {
    setSession(getSession());
    Promise.allSettled([apiGet(`/v1/hospitals/${slug}/inventory`), apiGet("/v1/hospitals/")]).then(([inv, hosp]) => {
      if (inv.status === "fulfilled") {
        const value = inv.value;
        setInventory(value?.items ?? (Array.isArray(value) ? value : []));
      }
      if (hosp.status === "fulfilled") setHospitals(Array.isArray(hosp.value) ? hosp.value : hosp.value?.hospitals ?? []);
      setLoading(false);
    });
  }, [slug]);

  const filtered = inventory.filter((i) => {
    const matchesSearch = i.name.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "All" || statusOf(i) === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  const statusBadge: Record<string, string> = {
    critical: "bg-red-600 text-white",
    warning: "bg-amber-600 text-white",
    ok: "bg-green-600 text-white",
  };

  function addMedicine() {
    if (!newMed.medicine.trim()) return;
    const stock = Number(newMed.stock) || 0;
    setInventory((list) => [
      ...list,
      {
        name: newMed.medicine,
        current_stock: stock,
        daily_usage_rate: newMed.used_per_day ? Number(newMed.used_per_day) : undefined,
        status: stock === 0 ? "critical" : "ok",
      },
    ]);
    setNewMed({ medicine: "", stock: "", used_per_day: "" });
    setShowAdd(false);
  }

  function openDistress(item: InventoryItem) {
    setOverlayItem(item);
    setQuantity("");
    setReason("");
    setResult(null);
    setSendError(null);
    setChecking([]);
  }

  async function sendDistress() {
    if (!overlayItem || !quantity) return;
    setSending(true);
    setSendError(null);
    setChecking([]);

    const others = hospitals.filter((h) => h.slug !== slug).slice(0, 4);
    others.forEach((h, i) => {
      setTimeout(() => setChecking((c) => [...c, h.name]), (i + 1) * 500);
    });

    try {
      const data = await apiPost(`/v1/hospitals/${slug}/distress`, {
        medicine: overlayItem.name,
        quantity_needed: Number(quantity),
        urgency: overlayItem.status ?? "critical",
        reason: reason || undefined,
      });
      setResult(data);
      setDistressSentCount((n) => n + 1);
    } catch (e) {
      setSendError(e instanceof Error ? e.message : "Could not send the distress signal. Try again.");
    } finally {
      setSending(false);
    }
  }

  const stats = [
    { label: "Medicines", value: inventory.length },
    { label: "Critical", value: inventory.filter((i) => statusOf(i) === "critical").length },
    { label: "Warning", value: inventory.filter((i) => statusOf(i) === "warning").length },
    { label: "Active Distress", value: distressSentCount },
  ];

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-stone-900">{session?.hospital_name ?? slug}</h1>
          <p className="text-sm text-stone-500">{session?.name ?? "Staff"}{session?.role ? ` - ${formatRole(session.role)}` : ""}</p>
        </div>
        <button onClick={() => clearSession()} className="clay-btn-secondary flex items-center gap-1 rounded-xl px-3 py-2 text-sm">
          <LogOut size={14} /> Log out
        </button>
      </div>

      <div className="clay-card-flat flex flex-wrap gap-1 rounded-2xl p-1.5">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`rounded-xl px-4 py-2 text-sm font-medium ${tab === t ? "tab-active" : "tab-inactive"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab !== "Inventory" ? (
        <div className="clay-card p-8 text-center text-sm text-stone-500">
          {tab} isn't wired up yet - this tab is a placeholder until the matching backend endpoint exists.
        </div>
      ) : loading ? (
        <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={16} className="animate-spin" /> Loading inventory...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {stats.map((s) => (
              <div key={s.label} className="clay-card p-5 text-center">
                <div className="text-2xl font-extrabold text-amber-900">{s.value}</div>
                <div className="text-xs text-stone-500">{s.label}</div>
              </div>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="clay-input flex items-center gap-2 px-3 py-2">
              <Search size={14} className="text-stone-400" />
              <input className="w-40 bg-transparent text-sm outline-none" placeholder="Search medicine..." value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <select className="clay-input px-3 py-2 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option>All</option>
              <option>Critical</option>
              <option>Warning</option>
              <option>Ok</option>
            </select>
            <button onClick={() => setShowAdd((v) => !v)} className="clay-btn flex items-center gap-1 rounded-xl px-4 py-2 text-sm">
              <Plus size={16} /> Add Medicine
            </button>
          </div>

          {showAdd && (
            <div className="clay-card-flat flex flex-wrap items-end gap-2 rounded-2xl p-4">
              <input className="clay-input flex-1 px-3 py-2 text-sm" placeholder="Medicine name" value={newMed.medicine} onChange={(e) => setNewMed((m) => ({ ...m, medicine: e.target.value }))} />
              <input className="clay-input w-24 px-3 py-2 text-sm" placeholder="Stock" type="number" value={newMed.stock} onChange={(e) => setNewMed((m) => ({ ...m, stock: e.target.value }))} />
              <input className="clay-input w-28 px-3 py-2 text-sm" placeholder="Used/day" type="number" value={newMed.used_per_day} onChange={(e) => setNewMed((m) => ({ ...m, used_per_day: e.target.value }))} />
              <button onClick={addMedicine} className="clay-btn rounded-lg px-3 py-2 text-sm">Add</button>
              <p className="w-full text-xs text-stone-400">Added locally only - connect a create-inventory endpoint to persist this.</p>
            </div>
          )}

          <div className="clay-card p-6">
            <div className="divide-y divide-stone-200">
              {filtered.length === 0 && <p className="py-4 text-sm text-stone-500">No medicines match your filters.</p>}
              {filtered.map((item, i) => {
                const s = statusOf(item);
                return (
                  <div key={i} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
                    <span className="font-medium text-stone-800">{item.name}</span>
                    <span className="text-stone-500">{item.current_stock} in stock</span>
                    {item.daily_usage_rate !== undefined && <span className="text-stone-500">{item.daily_usage_rate}/day</span>}
                    {item.days_left !== undefined && <span className="text-stone-500">{item.days_left} d left</span>}
                    <span className={`clay-pill px-2.5 py-1 text-xs font-bold ${statusBadge[s] ?? "bg-stone-300 text-stone-700"}`}>
                      {(item.status ?? "-").toUpperCase()}
                    </span>
                    {s === "critical" ? (
                      <button onClick={() => openDistress(item)} className="clay-btn flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs">
                        <Radio size={13} /> Distress
                      </button>
                    ) : s === "warning" ? (
                      <button
                        onClick={() => alert("Order request queued (demo only - connect a supplier-order endpoint to send this for real).")}
                        className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs"
                      >
                        <Send size={13} /> Order
                      </button>
                    ) : (
                      <span className="text-xs text-stone-300">-</span>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="clay-card p-6">
            <h2 className="mb-2 font-bold text-stone-900">Recent Stock Movements</h2>
            <p className="text-sm text-stone-500">This will show live activity once your backend exposes a stock-movements endpoint.</p>
          </div>

          <div className="space-y-1 text-sm text-stone-400">
            <p>Medical Staff - Locked (Doctors Only)</p>
            <p>Patient Care - Locked (Nurses Only)</p>
          </div>
        </>
      )}

      {overlayItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/40 p-4">
          <div className="clay-card w-full max-w-md space-y-4 p-6">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-lg font-bold text-stone-900">
                <TriangleAlert size={18} className="text-red-600" /> Send Distress Signal
              </h2>
              <button onClick={() => setOverlayItem(null)} className="text-stone-400 hover:text-stone-700">
                <X size={18} />
              </button>
            </div>

            {!result ? (
              <>
                <div className="clay-card-flat space-y-1 rounded-2xl p-4 text-sm">
                  <div className="font-semibold text-stone-800">{overlayItem.name}</div>
                  <div className="text-stone-500">Current Stock: {overlayItem.current_stock}</div>
                  {overlayItem.daily_usage_rate !== undefined && <div className="text-stone-500">Daily Usage: {overlayItem.daily_usage_rate}/day</div>}
                  {overlayItem.days_left !== undefined && <div className="text-stone-500">Stock-out in: ~{overlayItem.days_left} days</div>}
                </div>

                <label className="block space-y-1.5">
                  <span className="text-sm font-medium text-stone-600">Quantity Needed</span>
                  <input type="number" className="clay-input w-full px-4 py-2.5" value={quantity} onChange={(e) => setQuantity(e.target.value)} />
                </label>

                <label className="block space-y-1.5">
                  <span className="text-sm font-medium text-stone-600">Reason (optional)</span>
                  <textarea className="clay-input min-h-[80px] w-full resize-none p-3" value={reason} onChange={(e) => setReason(e.target.value)} />
                </label>

                {sending && (
                  <div className="clay-card-flat space-y-1 rounded-2xl p-4 text-sm text-stone-600">
                    <p className="flex items-center gap-2 font-medium"><Loader2 size={14} className="animate-spin" /> Gemma 4 is analyzing nearby hospitals...</p>
                    {checking.map((name, i) => (
                      <p key={i} className="pl-6 text-xs text-stone-500">Checking {name}...</p>
                    ))}
                  </div>
                )}

                {sendError && <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{sendError}</div>}

                <div className="flex justify-end gap-2">
                  <button onClick={() => setOverlayItem(null)} className="clay-btn-secondary rounded-xl px-4 py-2 text-sm">Cancel</button>
                  <button onClick={sendDistress} disabled={sending || !quantity} className="clay-btn flex items-center gap-2 rounded-xl px-4 py-2 text-sm">
                    {sending ? <Loader2 size={14} className="animate-spin" /> : <Radio size={14} />} Send Distress Signal
                  </button>
                </div>
              </>
            ) : (
              <div className="space-y-3">
                <p className="font-semibold text-green-700">Distress Signal Sent!</p>
                {result.signal_id && <p className="text-xs text-stone-400">Signal ID: {result.signal_id}</p>}
                {result.ai_recommendation && (
                  <div className="clay-card-flat rounded-xl p-4 text-sm italic text-stone-700">{result.ai_recommendation}</div>
                )}
                {result.suggested_source && (
                  <p className="text-sm text-stone-600">Suggested source: <span className="font-semibold">{result.suggested_source}</span></p>
                )}
                {result.nearby_hospitals && result.nearby_hospitals.length > 0 && (
                  <div className="space-y-1.5">
                    {result.nearby_hospitals.map((h, i) => (
                      <div key={i} className="flex items-center justify-between text-sm text-stone-600">
                        <span>{h.name}</span>
                        {h.distance_km !== undefined && <span className="text-stone-500">{h.distance_km} km</span>}
                      </div>
                    ))}
                  </div>
                )}
                <button onClick={() => setOverlayItem(null)} className="clay-btn w-full rounded-xl px-4 py-2 text-sm">Back to Inventory</button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

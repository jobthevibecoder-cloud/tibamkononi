"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, LayoutDashboard, ClipboardList, Megaphone, BarChart3, Download, Search } from "lucide-react";
import { apiGet } from "@/lib/api";
import { getSession } from "@/lib/session";
import type { Session } from "@/lib/session";

type DashboardStats = {
  county_name?: string;
  total_hospitals?: number;
  total_beds?: number;
  beds_available?: number;
  occupancy_rate?: number;
  critical_alerts?: number;
  stock_warnings?: number;
};

type HospitalRow = {
  slug: string;
  name: string;
  type?: string;
  status?: string;
  performance_score?: number;
  alerts?: number;
  warnings?: number;
  distress_count?: number;
};

export default function CountyDashboard() {
  const [session, setSession] = useState<Session | null>(null);
  const [stats, setStats] = useState<DashboardStats>({});
  const [hospitals, setHospitals] = useState<HospitalRow[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    setSession(getSession());
    Promise.allSettled([
      apiGet("/v1/county/dashboard"),
      apiGet("/v1/county/hospitals"),
      apiGet("/v1/county/approvals"),
    ]).then(([dash, hosp, approvals]) => {
      if (dash.status === "fulfilled") setStats(dash.value ?? {});
      if (hosp.status === "fulfilled") setHospitals(Array.isArray(hosp.value) ? hosp.value : hosp.value?.hospitals ?? []);
      if (approvals.status === "fulfilled") {
        const list = approvals.value?.pending ?? (Array.isArray(approvals.value) ? approvals.value : []);
        setPendingCount(approvals.value?.total ?? list.length);
      }
      setLoading(false);
    });
  }, []);

  const statusColor: Record<string, string> = { green: "bg-green-500", yellow: "bg-amber-500", red: "bg-red-500" };

  const filtered = hospitals.filter((h) => {
    const matchesSearch = h.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === "All" || h.status === filter.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="clay-card-flat flex h-12 w-12 items-center justify-center rounded-2xl text-amber-900">
            <LayoutDashboard size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-stone-900">
              {session?.name ? `${session.name} - ` : ""}{stats.county_name ?? "County"} Health Director
            </h1>
            <p className="text-sm text-stone-500">{new Date().toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" })}</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={16} className="animate-spin" /> Loading county data...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: "Hospitals", value: stats.total_hospitals ?? "-" },
              { label: "Beds Available", value: stats.beds_available ?? "-" },
              { label: "Critical", value: stats.critical_alerts ?? "-" },
              { label: "Stock Warnings", value: stats.stock_warnings ?? "-" },
            ].map((s) => (
              <div key={s.label} className="clay-card p-5 text-center">
                <div className="text-2xl font-extrabold text-amber-900">{s.value}</div>
                <div className="text-xs text-stone-500">{s.label}</div>
              </div>
            ))}
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <Link href="/county/approvals" className="clay-card flex items-center gap-3 p-4 transition-transform hover:-translate-y-0.5">
              <ClipboardList size={20} className="text-amber-900" />
              <span className="font-semibold text-stone-800">Pending Approvals ({pendingCount})</span>
            </Link>
            <Link href="/county/announcements/new" className="clay-card flex items-center gap-3 p-4 transition-transform hover:-translate-y-0.5">
              <Megaphone size={20} className="text-amber-900" />
              <span className="font-semibold text-stone-800">Post Announcement</span>
            </Link>
            <Link href="/county/watchlist" className="clay-card flex items-center gap-3 p-4 transition-transform hover:-translate-y-0.5">
              <BarChart3 size={20} className="text-amber-900" />
              <span className="font-semibold text-stone-800">Weekly Watchlist</span>
            </Link>
            <button
              onClick={() => {
                const blob = new Blob([JSON.stringify({ stats, hospitals }, null, 2)], { type: "application/json" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "county-report.json";
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="clay-card flex items-center gap-3 p-4 text-left transition-transform hover:-translate-y-0.5"
            >
              <Download size={20} className="text-amber-900" />
              <span className="font-semibold text-stone-800">Download Report</span>
            </button>
          </div>

          <div className="clay-card p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h2 className="font-bold text-stone-900">All Hospitals (A-Z)</h2>
              <div className="flex gap-2">
                <div className="clay-input flex items-center gap-2 px-3 py-2">
                  <Search size={14} className="text-stone-400" />
                  <input
                    className="w-40 bg-transparent text-sm outline-none"
                    placeholder="Search hospitals..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
                <select className="clay-input px-3 py-2 text-sm" value={filter} onChange={(e) => setFilter(e.target.value)}>
                  <option>All</option>
                  <option value="green">Green</option>
                  <option value="yellow">Yellow</option>
                  <option value="red">Red</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              {filtered.length === 0 && <p className="text-sm text-stone-500">No hospitals match.</p>}
              {filtered
                .sort((a, b) => a.name.localeCompare(b.name))
                .map((h) => (
                  <Link key={h.slug} href={`/county/hospitals/${h.slug}`} className="clay-card-flat flex items-center justify-between rounded-xl px-4 py-3 transition-colors hover:bg-white/80">
                    <div className="flex items-center gap-3">
                      <span className={`h-2.5 w-2.5 rounded-full ${statusColor[h.status ?? ""] ?? "bg-stone-400"}`} />
                      <div>
                        <div className="text-sm font-semibold text-stone-800">{h.name}</div>
                        <div className="text-xs text-stone-500">
                          {h.type ?? "Hospital"}
                          {h.alerts ? ` - ${h.alerts} critical` : ""}
                          {h.warnings ? ` - ${h.warnings} warnings` : ""}
                          {h.distress_count ? ` - ${h.distress_count} distress` : ""}
                        </div>
                      </div>
                    </div>
                    <span className="text-sm font-bold text-amber-900">Score: {h.performance_score ?? "-"}</span>
                  </Link>
                ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

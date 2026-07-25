"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, ArrowLeft, Phone } from "lucide-react";
import { apiGet } from "@/lib/api";

type Medicine = {
  id?: string;
  name: string;
  current_stock: number;
  unit?: string;
  minimum_threshold?: number;
  daily_usage_rate?: number;
  days_left?: number;
  status?: string;
  last_restock?: string;
};

type StaffMember = {
  id?: string;
  name: string;
  role: string;
  specialization?: string;
  attendance_rate?: number;
};

type DistressSignal = { id: string; medicine: string; destination?: string; status: string };

type HospitalDetail = {
  hospital?: {
    id?: string;
    name: string;
    slug?: string;
    type?: string;
    location?: string;
    phone?: string;
    director?: string;
    performance_score?: number;
  };
  medicines?: Medicine[];
  staff?: StaffMember[];
  ai_summary?: string;
  ai_recommendations?: string[];
  distress_signals?: DistressSignal[];
  flags?: string[];
};

export default function HospitalDeepDivePage({ params }: { params: { slug: string } }) {
  const { slug } = params;
  const [data, setData] = useState<HospitalDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionsTaken, setActionsTaken] = useState<Record<number, boolean>>({});

  useEffect(() => {
    apiGet(`/v1/county/hospitals/${slug}`)
      .then((d) => setData(d))
      .catch((e) => setError(e instanceof Error ? e.message : "Could not load hospital details."))
      .finally(() => setLoading(false));
  }, [slug]);

  const statusBadge: Record<string, string> = {
    critical: "bg-red-600 text-white",
    warning: "bg-amber-600 text-white",
    ok: "bg-green-600 text-white",
  };

  const hospital = data?.hospital;
  const score = hospital?.performance_score ?? 0;
  const scoreColor = score >= 70 ? "text-green-600" : score >= 40 ? "text-amber-600" : "text-red-600";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link href="/county" className="flex items-center gap-1 text-sm font-medium text-stone-500 hover:text-amber-900">
        <ArrowLeft size={14} /> Back to Hospitals
      </Link>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={16} className="animate-spin" /> Loading hospital...</div>
      ) : error || !hospital ? (
        <div className="clay-card p-6 text-sm text-red-700">{error ?? "Hospital not found."}</div>
      ) : (
        <>
          <div className="clay-card space-y-1 p-6">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h1 className="text-2xl font-bold text-stone-900">{hospital.name}</h1>
              <span className={`text-lg font-bold ${scoreColor}`}>Score: {score}/100</span>
            </div>
            <p className="text-sm text-stone-500">{hospital.type} - {hospital.location}</p>
            {hospital.director && (
              <p className="flex items-center gap-1.5 text-sm text-stone-600">
                Director: {hospital.director}
                {hospital.phone && (
                  <a href={`tel:${hospital.phone}`} className="flex items-center gap-1 text-amber-800">
                    <Phone size={12} /> {hospital.phone}
                  </a>
                )}
              </p>
            )}
          </div>

          <div className="clay-card space-y-2 p-6">
            <h2 className="font-bold text-stone-900">Active Distress Signals</h2>
            {data?.distress_signals && data.distress_signals.length > 0 ? (
              data.distress_signals.map((d) => (
                <div key={d.id} className="clay-card-flat flex items-center justify-between rounded-xl px-4 py-2.5 text-sm">
                  <span>{d.id} - {d.medicine}{d.destination ? ` -> ${d.destination}` : ""}</span>
                  <span className={`clay-pill px-2.5 py-1 text-xs font-bold ${d.status === "Fulfilled" ? "bg-green-600 text-white" : "bg-amber-600 text-white"}`}>
                    {d.status}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-sm text-stone-500">No active distress signals.</p>
            )}
          </div>

          {data?.medicines && data.medicines.length > 0 && (
            <div className="clay-card space-y-2 p-6">
              <h2 className="font-bold text-stone-900">Inventory Status</h2>
              <div className="divide-y divide-stone-200">
                {data.medicines.map((item, i) => (
                  <div key={i} className="flex flex-wrap items-center justify-between gap-2 py-2.5 text-sm">
                    <span className="font-medium text-stone-800">{item.name}</span>
                    <span className="text-stone-500">{item.current_stock} {item.unit ?? "in stock"}</span>
                    {item.daily_usage_rate !== undefined && <span className="text-stone-500">{item.daily_usage_rate}/day</span>}
                    {item.days_left !== undefined && <span className="text-stone-500">{item.days_left} d left</span>}
                    <span className={`clay-pill px-2.5 py-1 text-xs font-bold ${statusBadge[(item.status ?? "").toLowerCase()] ?? "bg-stone-300 text-stone-700"}`}>
                      {(item.status ?? "-").toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {data?.ai_summary && (
            <div className="clay-card space-y-2 p-6">
              <h2 className="font-bold text-stone-900">Gemma 4 AI Analysis</h2>
              <p className="clay-card-flat rounded-xl p-4 text-sm italic text-stone-700">{data.ai_summary}</p>
            </div>
          )}

          {data?.ai_recommendations && data.ai_recommendations.length > 0 && (
            <div className="clay-card space-y-3 p-6">
              <h2 className="font-bold text-stone-900">AI Recommendations</h2>
              {data.ai_recommendations.map((text, i) => (
                <div key={i} className="clay-card-flat flex flex-wrap items-center justify-between gap-2 rounded-xl p-4 text-sm">
                  <span className="text-stone-700">{text}</span>
                  <button
                    onClick={() => setActionsTaken((a) => ({ ...a, [i]: true }))}
                    disabled={actionsTaken[i]}
                    className="clay-btn rounded-lg px-3 py-1.5 text-xs disabled:opacity-50"
                  >
                    {actionsTaken[i] ? "Actioned" : "Mark Actioned"}
                  </button>
                </div>
              ))}
            </div>
          )}

          {data?.staff && data.staff.length > 0 && (
            <div className="clay-card space-y-2 p-6">
              <h2 className="font-bold text-stone-900">Staff</h2>
              {data.staff.map((s, i) => (
                <div key={i} className="clay-card-flat flex items-center justify-between rounded-xl px-4 py-2.5 text-sm">
                  <span>{s.name} - {s.role}{s.specialization ? ` (${s.specialization})` : ""}</span>
                  {s.attendance_rate !== undefined && (
                    <span className={s.attendance_rate < 70 ? "font-semibold text-red-600" : "text-green-600"}>
                      {s.attendance_rate}% attendance
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}

          {data?.flags && data.flags.length > 0 && (
            <div className="clay-card space-y-3 p-6">
              <h2 className="font-bold text-red-700">Flag for Review</h2>
              <ul className="list-inside list-disc text-sm text-stone-600">
                {data.flags.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}

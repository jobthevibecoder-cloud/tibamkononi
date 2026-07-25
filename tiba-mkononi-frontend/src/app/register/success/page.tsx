"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CircleCheck, Building2, LogIn, ClipboardList } from "lucide-react";

type RegistrationSummary = {
  hospital_id?: string;
  slug?: string;
  status?: string;
  name?: string;
  physical_address?: string;
  license_number?: string;
  type?: string;
  director_name?: string;
  buildings_count?: number;
  beds_total?: number;
  amenities?: string[];
};

export default function RegisterSuccessPage() {
  const [data, setData] = useState<RegistrationSummary | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const raw = sessionStorage.getItem("tiba_registration");
    if (raw) {
      try {
        setData(JSON.parse(raw));
      } catch {
        setData(null);
      }
    }
    setLoaded(true);
  }, []);

  if (loaded && !data) {
    return (
      <div className="mx-auto max-w-md">
        <div className="clay-card flex flex-col items-center gap-3 p-10 text-center">
          <p className="text-sm text-stone-500">No recent registration found.</p>
          <Link href="/register" className="clay-btn rounded-xl px-5 py-2.5 text-sm font-semibold">
            Register a Hospital
          </Link>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="mx-auto max-w-md">
      <div className="clay-card flex flex-col items-center gap-4 p-10 text-center">
        <CircleCheck size={44} className="text-green-600" />
        <h1 className="text-xl font-bold text-stone-900">Registration Submitted!</h1>

        <div className="clay-card-flat w-full space-y-2 rounded-2xl p-6 text-left">
          <div className="flex items-center gap-2 font-bold text-stone-900">
            <Building2 size={18} className="text-amber-900" /> {data.name || "Your Hospital"}
          </div>
          <p className="text-sm text-stone-500">{data.physical_address}</p>
          <span className="clay-pill inline-block bg-amber-600 px-3 py-1 text-xs font-bold text-white">
            Status: Pending County Director Approval
          </span>
          <p className="pt-2 text-sm text-stone-600">
            Your hospital will be reviewed by the County Health Director. You will be notified once approved.
          </p>
        </div>

        <div className="w-full text-left">
          <h2 className="mb-2 text-sm font-bold text-stone-900">What happens next?</h2>
          <ol className="space-y-1.5 text-sm text-stone-600">
            <li>1. License verification</li>
            <li>2. County Director approval</li>
            <li>3. You receive access to your dashboard</li>
          </ol>
        </div>

        <div className="flex flex-wrap justify-center gap-3 pt-2">
          <Link href="/login" className="clay-btn flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold">
            <LogIn size={16} /> Go to Login
          </Link>
          <button onClick={() => setShowDetails((v) => !v)} className="clay-btn-secondary flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold">
            <ClipboardList size={16} /> {showDetails ? "Hide" : "View"} Details
          </button>
        </div>

        {showDetails && (
          <div className="w-full space-y-1 rounded-2xl bg-stone-100 p-4 text-left text-xs text-stone-500">
            <div>Hospital ID: {data.hospital_id ?? "n/a"}</div>
            <div>Slug: {data.slug ?? "n/a"}</div>
            <div>License: {data.license_number}</div>
            <div>Type: {data.type}</div>
            <div>Director: {data.director_name}</div>
            <div>Buildings: {data.buildings_count}</div>
            <div>Total Beds: {data.beds_total}</div>
            <div>Amenities: {(data.amenities ?? []).join(", ") || "none"}</div>
          </div>
        )}
      </div>
    </div>
  );
}

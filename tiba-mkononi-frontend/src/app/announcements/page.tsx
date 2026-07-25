"use client";

import { useEffect, useState } from "react";
import { Megaphone, Pin, Loader2 } from "lucide-react";
import { apiGet } from "@/lib/api";

type Announcement = {
  id: string | number;
  type: string;
  title: string;
  body: string;
  published_at: string;
  pinned?: boolean;
};

const FILTERS = ["All", "Medicine Delivery", "Funding", "Inspection", "Health Alert"];

const TYPE_COLORS: Record<string, string> = {
  "Medicine Delivery": "bg-green-600",
  Funding: "bg-amber-600",
  Inspection: "bg-stone-600",
  "Health Alert": "bg-red-600",
};

export default function AnnouncementsPage() {
  const [filter, setFilter] = useState("All");
  const [items, setItems] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet("/v1/announcements/?county_code=MSA")
      .then((data) => setItems(Array.isArray(data) ? data : data?.announcements ?? []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter === "All" ? items : items.filter((a) => a.type === filter);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="clay-card-flat flex h-12 w-12 items-center justify-center rounded-2xl text-amber-900">
          <Megaphone size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">County Announcements</h1>
          <p className="text-sm text-stone-500">Medicine deliveries, funding, inspections and health alerts.</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`clay-pill px-4 py-2 text-sm font-medium ${filter === f ? "tab-active" : "clay-card-flat text-stone-600"}`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={16} className="animate-spin" /> Loading announcements...</div>
      ) : filtered.length === 0 ? (
        <div className="clay-card p-8 text-center text-sm text-stone-500">No announcements yet.</div>
      ) : (
        <div className="space-y-4">
          {filtered.map((a) => (
            <div key={a.id} className="clay-card space-y-2 p-5">
              <div className="flex items-center justify-between">
                <span className={`clay-pill px-3 py-1 text-xs font-bold text-white ${TYPE_COLORS[a.type] ?? "bg-stone-500"}`}>
                  {a.type}
                </span>
                {a.pinned && <Pin size={16} className="text-amber-700" />}
              </div>
              <h3 className="font-bold text-stone-900">{a.title}</h3>
              <p className="text-sm text-stone-600">{a.body}</p>
              <p className="text-xs text-stone-400">{new Date(a.published_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, ArrowLeft, Megaphone, Save } from "lucide-react";
import { apiPost } from "@/lib/api";

const TYPES = ["Medicine Delivery", "Funding Allocation", "Inspection Notice", "Health Alert", "Training/Event", "General Update"];
const TARGETS = [
  { value: "ALL", label: "All Mombasa Hospitals" },
  { value: "SPECIFIC_HOSPITALS", label: "Specific Hospitals" },
  { value: "BY_SUBCOUNTY", label: "By Sub-County" },
  { value: "BY_TYPE", label: "By Type" },
];
const DRAFT_KEY = "announcement_draft";

export default function NewAnnouncementPage() {
  const [type, setType] = useState(TYPES[0]);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [targetType, setTargetType] = useState(TARGETS[0].value);
  const [pinned, setPinned] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [posted, setPosted] = useState(false);
  const [draftFound, setDraftFound] = useState(false);
  const [savedNote, setSavedNote] = useState(false);

  useEffect(() => {
    if (sessionStorage.getItem(DRAFT_KEY)) setDraftFound(true);
  }, []);

  function restoreDraft() {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (!raw) return;
    try {
      const d = JSON.parse(raw);
      setType(d.type ?? TYPES[0]);
      setTitle(d.title ?? "");
      setBody(d.body ?? "");
      setTargetType(d.targetType ?? TARGETS[0].value);
      setPinned(!!d.pinned);
    } catch {
      // ignore corrupt draft
    }
    setDraftFound(false);
  }

  function discardDraft() {
    sessionStorage.removeItem(DRAFT_KEY);
    setDraftFound(false);
  }

  function saveDraft() {
    sessionStorage.setItem(DRAFT_KEY, JSON.stringify({ type, title, body, targetType, pinned }));
    setSavedNote(true);
    setTimeout(() => setSavedNote(false), 2500);
  }

  async function post() {
    if (!title.trim() || !body.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await apiPost("/v1/announcements/create", { type, title, body, target_type: targetType, is_pinned: pinned });
      sessionStorage.removeItem(DRAFT_KEY);
      setPosted(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not post the announcement. Try again.");
    } finally {
      setLoading(false);
    }
  }

  if (posted) {
    return (
      <div className="mx-auto max-w-md">
        <div className="clay-card flex flex-col items-center gap-3 p-10 text-center">
          <Megaphone size={40} className="text-amber-900" />
          <h2 className="text-xl font-bold text-stone-900">Announcement Posted</h2>
          <p className="text-sm text-stone-500">Hospitals will see it on the Announcements board.</p>
          <Link href="/announcements" className="clay-btn rounded-xl px-5 py-2.5 text-sm font-semibold">View Announcements</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <Link href="/county" className="flex items-center gap-1 text-sm font-medium text-stone-500 hover:text-amber-900">
        <ArrowLeft size={14} /> Back to Dashboard
      </Link>

      <h1 className="text-2xl font-bold text-stone-900">Post New Announcement</h1>

      {draftFound && (
        <div className="clay-card-flat flex items-center justify-between gap-3 rounded-2xl p-4 text-sm">
          <span>A saved draft was found.</span>
          <div className="flex gap-2">
            <button onClick={restoreDraft} className="clay-btn rounded-lg px-3 py-1.5 text-xs">Restore</button>
            <button onClick={discardDraft} className="clay-btn-secondary rounded-lg px-3 py-1.5 text-xs">Discard</button>
          </div>
        </div>
      )}

      <div className="clay-card space-y-4 p-6">
        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-stone-600">Type</span>
          <select className="clay-input w-full px-4 py-2.5" value={type} onChange={(e) => setType(e.target.value)}>
            {TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </label>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-stone-600">Title</span>
          <input className="clay-input w-full px-4 py-2.5" value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-stone-600">Message</span>
          <textarea className="clay-input min-h-[160px] w-full resize-none p-4" value={body} onChange={(e) => setBody(e.target.value)} />
        </label>

        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-stone-600">Target</span>
          <select className="clay-input w-full px-4 py-2.5" value={targetType} onChange={(e) => setTargetType(e.target.value)}>
            {TARGETS.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-2">
          <input type="checkbox" checked={pinned} onChange={(e) => setPinned(e.target.checked)} className="h-4 w-4" />
          <span className="text-sm text-stone-600">Pin to top of announcements board</span>
        </label>

        {error && <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <div className="flex flex-wrap gap-3 pt-2">
          <button
            onClick={post}
            disabled={loading || !title.trim() || !body.trim()}
            className="clay-btn flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <Megaphone size={16} />}
            {loading ? "Posting..." : "Post Announcement"}
          </button>
          <button onClick={saveDraft} className="clay-btn-secondary flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold">
            <Save size={16} /> {savedNote ? "Saved!" : "Save Draft"}
          </button>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { Loader2, Siren, Phone, MapPin, TriangleAlert, Send } from "lucide-react";
import { apiPost, ApiError } from "@/lib/api";

type Hospital = {
  id?: string;
  name: string;
  slug?: string;
  distance_km?: number;
  eta_minutes?: number;
  phone?: string;
  latitude?: number;
  longitude?: number;
};

type EmergencyResult = {
  emergency_id?: string;
  severity?: string;
  dispatch_message?: string;
  hospitals?: Hospital[];
};

const DEFAULT_COORDS = { latitude: -4.0845, longitude: 39.6672 };

export default function EmergencyPage() {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState<"sw" | "en">("sw");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EmergencyResult | null>(null);
  const [dispatching, setDispatching] = useState<string | null>(null);
  const [dispatched, setDispatched] = useState<Record<string, boolean>>({});

  async function getCoords(): Promise<{ latitude: number; longitude: number }> {
    return new Promise((resolve) => {
      if (!navigator.geolocation) return resolve(DEFAULT_COORDS);
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
        () => resolve(DEFAULT_COORDS),
        { timeout: 4000 }
      );
    });
  }

  async function handleSubmit() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setDispatched({});
    try {
      const coords = await getCoords();
      const data = await apiPost("/v1/emergency/analyze", {
        input_type: "text",
        latitude: coords.latitude,
        longitude: coords.longitude,
        text,
        language,
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not reach the emergency service. Try again.");
    } finally {
      setLoading(false);
    }
  }

  async function dispatchTo(hospital: Hospital) {
    if (!result?.emergency_id || !hospital.id) return;
    const key = hospital.id;
    setDispatching(key);
    try {
      await apiPost("/v1/emergency/dispatch", { emergency_id: result.emergency_id, hospital_id: hospital.id });
      setDispatched((d) => ({ ...d, [key]: true }));
    } catch {
      // best-effort for the demo
    } finally {
      setDispatching(null);
    }
  }

  const severity = (result?.severity || "").toUpperCase();
  const severityClass =
    severity === "SEVERE"
      ? "bg-red-600 text-white"
      : severity === "MODERATE"
      ? "bg-amber-600 text-white"
      : "bg-stone-300 text-stone-700";

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="clay-card-flat flex h-12 w-12 items-center justify-center rounded-2xl text-red-600">
          <Siren size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">Emergency Response</h1>
          <p className="text-sm text-stone-500">Describe what is happening - we will find the nearest hospital that can help.</p>
        </div>
      </div>

      <div className="clay-card space-y-4 p-6">
        <textarea
          className="clay-input min-h-[140px] w-full resize-none p-4 text-stone-900 placeholder:text-stone-400"
          placeholder="Eleza dharura yako... (mfano: Mtu amepata ajali ya gari, anavuja damu sana)"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex gap-2">
            {(["sw", "en"] as const).map((lang) => (
              <button
                key={lang}
                onClick={() => setLanguage(lang)}
                className={`clay-pill px-4 py-1.5 text-sm font-medium transition-colors ${
                  language === lang ? "tab-active" : "clay-card-flat text-stone-500"
                }`}
              >
                {lang === "sw" ? "Kiswahili" : "English"}
              </button>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !text.trim()}
            className="clay-btn flex items-center gap-2 rounded-2xl px-6 py-3 font-semibold"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Siren size={18} />}
            {loading ? "Sending Alert..." : "Send Emergency Alert"}
          </button>
        </div>

        {error && (
          <div className="flex items-center gap-2 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">
            <TriangleAlert size={16} /> {error}
          </div>
        )}
      </div>

      {result && (
        <div className="space-y-4">
          <div className="clay-card space-y-3 p-6">
            <span className={`clay-pill inline-block px-4 py-1 text-sm font-bold ${severityClass}`}>
              {severity || "ANALYZED"}
            </span>
            {result.dispatch_message && (
              <div className="clay-card-flat p-4 text-sm leading-relaxed text-stone-800">
                {result.dispatch_message}
              </div>
            )}
          </div>

          {result.hospitals && result.hospitals.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-lg font-bold text-stone-900">Nearest Hospitals</h2>
              {result.hospitals.map((h, i) => {
                const canDispatch = Boolean(result.emergency_id && h.id);
                const key = h.id ?? String(i);
                return (
                  <div key={i} className="clay-card flex flex-wrap items-center justify-between gap-3 p-4">
                    <div>
                      <div className="font-semibold text-stone-900">{h.name}</div>
                      <div className="text-sm text-stone-500">
                        {h.distance_km !== undefined ? `${h.distance_km.toFixed(1)} km` : ""}
                        {h.eta_minutes !== undefined ? ` - ETA ${h.eta_minutes} min` : ""}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {h.phone && (
                        <a href={`tel:${h.phone}`} className="clay-btn-secondary flex items-center gap-1 rounded-xl px-3 py-2 text-sm">
                          <Phone size={14} /> Call
                        </a>
                      )}
                      {h.latitude && h.longitude && (
                        <a
                          href={`https://www.google.com/maps/dir/?api=1&destination=${h.latitude},${h.longitude}`}
                          target="_blank"
                          rel="noreferrer"
                          className="clay-btn flex items-center gap-1 rounded-xl px-3 py-2 text-sm"
                        >
                          <MapPin size={14} /> Map
                        </a>
                      )}
                      {canDispatch && (
                        <button
                          onClick={() => dispatchTo(h)}
                          disabled={dispatching === key || dispatched[key]}
                          className="clay-btn flex items-center gap-1 rounded-xl bg-red-700 px-3 py-2 text-sm disabled:opacity-60"
                        >
                          {dispatching === key ? (
                            <Loader2 size={14} className="animate-spin" />
                          ) : (
                            <Send size={14} />
                          )}
                          {dispatched[key] ? "Dispatched" : "Dispatch"}
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

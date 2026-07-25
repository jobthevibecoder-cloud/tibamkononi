"use client";

import { useState } from "react";
import { Loader2, Stethoscope, CircleCheck, TriangleAlert } from "lucide-react";
import { apiPost, ApiError } from "@/lib/api";

type Diagnosis = { name: string; confidence: number };
type Treatment = { medicine: string; dosage: string };
type TriageResult = {
  triage_level?: string;
  diagnoses?: Diagnosis[];
  recommended_tests?: string[];
  treatment?: Treatment[];
  self_care?: string[];
};

export default function TriagePage() {
  const [symptoms, setSymptoms] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("Female");
  const [language, setLanguage] = useState<"sw" | "en">("sw");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TriageResult | null>(null);

  async function handleSubmit() {
    if (!symptoms.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await apiPost("/v1/triage/analyze", {
        symptoms_text: symptoms,
        language,
        age: age ? Number(age) : undefined,
        gender,
      });
      setResult(data);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not analyze symptoms right now. Try again.");
    } finally {
      setLoading(false);
    }
  }

  const level = (result?.triage_level || "").toUpperCase();
  const levelClass =
    level === "EMERGENCY"
      ? "bg-red-600 text-white"
      : level === "URGENT"
      ? "bg-amber-600 text-white"
      : level === "ROUTINE"
      ? "bg-green-600 text-white"
      : "bg-stone-300 text-stone-700";

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="clay-card-flat flex h-12 w-12 items-center justify-center rounded-2xl text-amber-900">
          <Stethoscope size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">Self-Diagnosis</h1>
          <p className="text-sm text-stone-500">Describe your symptoms and get an AI-guided triage from Gemma 4.</p>
        </div>
      </div>

      <div className="clay-card space-y-4 p-6">
        <textarea
          className="clay-input min-h-[120px] w-full resize-none p-4 placeholder:text-stone-400"
          placeholder="Eleza dalili zako... (mfano: Nina homa, kikohozi na maumivu ya kichwa kwa siku 3)"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
        />

        <div className="grid grid-cols-2 gap-3">
          <input
            type="number"
            min={0}
            max={120}
            placeholder="Age"
            className="clay-input px-4 py-3 placeholder:text-stone-400"
            value={age}
            onChange={(e) => setAge(e.target.value)}
          />
          <select className="clay-input px-4 py-3" value={gender} onChange={(e) => setGender(e.target.value)}>
            <option>Female</option>
            <option>Male</option>
            <option>Other</option>
          </select>
        </div>

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
            disabled={loading || !symptoms.trim()}
            className="clay-btn flex items-center gap-2 rounded-2xl px-6 py-3 font-semibold"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Stethoscope size={18} />}
            {loading ? "Gemma 4 is analyzing..." : "Analyze Symptoms"}
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
          <div className="clay-card p-6">
            <span className={`clay-pill inline-block px-4 py-1 text-sm font-bold ${levelClass}`}>
              {level || "ANALYZED"}
            </span>
          </div>

          {result.diagnoses && result.diagnoses.length > 0 && (
            <div className="clay-card space-y-3 p-6">
              <h2 className="font-bold text-stone-900">Possible Diagnoses</h2>
              {result.diagnoses.map((d, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium text-stone-800">{d.name}</span>
                    <span className="text-stone-500">{Math.round(d.confidence * 100)}%</span>
                  </div>
                  <div className="clay-progress-track h-3 w-full">
                    <div className="clay-progress-fill h-full" style={{ width: `${Math.round(d.confidence * 100)}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}

          {result.recommended_tests && result.recommended_tests.length > 0 && (
            <div className="clay-card space-y-3 p-6">
              <h2 className="font-bold text-stone-900">Recommended Tests</h2>
              <div className="flex flex-wrap gap-2">
                {result.recommended_tests.map((t, i) => (
                  <span key={i} className="clay-pill clay-card-flat px-3 py-1.5 text-sm text-amber-900">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {result.treatment && result.treatment.length > 0 && (
            <div className="clay-card space-y-3 p-6">
              <h2 className="font-bold text-stone-900">Treatment</h2>
              <div className="divide-y divide-stone-200">
                {result.treatment.map((t, i) => (
                  <div key={i} className="flex justify-between py-2 text-sm">
                    <span className="font-medium text-stone-800">{t.medicine}</span>
                    <span className="text-stone-500">{t.dosage}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.self_care && result.self_care.length > 0 && (
            <div className="clay-card space-y-2 p-6">
              <h2 className="font-bold text-stone-900">Self-Care</h2>
              <ul className="space-y-2">
                {result.self_care.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-stone-700">
                    <CircleCheck size={16} className="mt-0.5 shrink-0 text-green-600" /> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

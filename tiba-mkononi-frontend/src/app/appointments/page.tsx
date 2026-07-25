"use client";

import { useEffect, useState } from "react";
import { Loader2, ClipboardList, CalendarDays, CircleCheck } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";

type HospitalOption = { slug: string; name: string; departments?: string[] };
type Slot = { time: string; available?: boolean };

export default function AppointmentsPage() {
  const [hospitals, setHospitals] = useState<HospitalOption[]>([]);
  const [hospitalSlug, setHospitalSlug] = useState("");
  const [department, setDepartment] = useState("");
  const [date, setDate] = useState("");
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState("");
  const [loadingSlots, setLoadingSlots] = useState(false);

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [nhif, setNhif] = useState("");

  const [booking, setBooking] = useState(false);
  const [reference, setReference] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet("/v1/hospitals/")
      .then((data) => setHospitals(Array.isArray(data) ? data : data?.hospitals ?? []))
      .catch(() => setHospitals([]));
  }, []);

  useEffect(() => {
    if (!hospitalSlug || !date) {
      setSlots([]);
      return;
    }
    setLoadingSlots(true);
    apiGet(`/v1/appointments/available?hospital_slug=${hospitalSlug}&date=${date}`)
      .then((data) => setSlots(Array.isArray(data) ? data : data?.slots ?? []))
      .catch(() => setSlots([]))
      .finally(() => setLoadingSlots(false));
  }, [hospitalSlug, date]);

  const selectedHospital = hospitals.find((h) => h.slug === hospitalSlug);

  async function confirmBooking() {
    if (!hospitalSlug || !selectedSlot || !name || !phone) return;
    setBooking(true);
    setError(null);
    try {
      const data = await apiPost("/v1/appointments/book", {
        hospital_slug: hospitalSlug,
        department,
        date,
        time: selectedSlot,
        patient_name: name,
        phone,
        nhif_number: nhif || undefined,
      });
      setReference(data?.reference ?? data?.booking_reference ?? "CONFIRMED");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not confirm booking. Try again.");
    } finally {
      setBooking(false);
    }
  }

  if (reference) {
    return (
      <div className="mx-auto max-w-md">
        <div className="clay-card flex flex-col items-center gap-3 p-10 text-center">
          <CircleCheck size={40} className="text-green-600" />
          <h2 className="text-xl font-bold text-stone-900">Appointment Confirmed</h2>
          <p className="text-sm text-stone-500">Your booking reference:</p>
          <div className="clay-card-flat rounded-xl px-6 py-3 text-lg font-bold tracking-wide text-amber-900">
            {reference}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="clay-card-flat flex h-12 w-12 items-center justify-center rounded-2xl text-amber-900">
          <ClipboardList size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">Book an Appointment</h1>
          <p className="text-sm text-stone-500">Pick a hospital, date and time that works for you.</p>
        </div>
      </div>

      <div className="clay-card space-y-4 p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block space-y-1.5">
            <span className="text-sm font-medium text-stone-600">Hospital</span>
            <select className="clay-input w-full px-4 py-2.5" value={hospitalSlug} onChange={(e) => setHospitalSlug(e.target.value)}>
              <option value="">Select hospital</option>
              {hospitals.map((h) => (
                <option key={h.slug} value={h.slug}>{h.name}</option>
              ))}
            </select>
          </label>
          <label className="block space-y-1.5">
            <span className="text-sm font-medium text-stone-600">Department</span>
            <select className="clay-input w-full px-4 py-2.5" value={department} onChange={(e) => setDepartment(e.target.value)}>
              <option value="">Select department</option>
              {(selectedHospital?.departments ?? ["General", "Maternity", "Pediatrics", "Dental"]).map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </label>
        </div>

        <label className="block space-y-1.5">
          <span className="flex items-center gap-1.5 text-sm font-medium text-stone-600">
            <CalendarDays size={14} /> Date
          </span>
          <input type="date" className="clay-input w-full px-4 py-2.5" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>

        {date && hospitalSlug && (
          <div className="space-y-2">
            <span className="text-sm font-medium text-stone-600">Available Slots</span>
            {loadingSlots ? (
              <div className="flex items-center gap-2 text-sm text-stone-500"><Loader2 size={14} className="animate-spin" /> Loading slots...</div>
            ) : slots.length === 0 ? (
              <p className="text-sm text-stone-500">No slots found for this date.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {slots.map((s) => (
                  <button
                    key={s.time}
                    disabled={s.available === false}
                    onClick={() => setSelectedSlot(s.time)}
                    className={`clay-pill px-4 py-2 text-sm font-medium disabled:opacity-30 ${
                      selectedSlot === s.time ? "tab-active" : "clay-card-flat text-stone-700"
                    }`}
                  >
                    {s.time}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {selectedSlot && (
          <div className="space-y-4 border-t border-stone-200 pt-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-stone-600">Patient Name</span>
                <input className="clay-input w-full px-4 py-2.5" value={name} onChange={(e) => setName(e.target.value)} />
              </label>
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-stone-600">Phone</span>
                <input className="clay-input w-full px-4 py-2.5" value={phone} onChange={(e) => setPhone(e.target.value)} />
              </label>
              <label className="block space-y-1.5 sm:col-span-2">
                <span className="text-sm font-medium text-stone-600">NHIF Number (optional)</span>
                <input className="clay-input w-full px-4 py-2.5" value={nhif} onChange={(e) => setNhif(e.target.value)} />
              </label>
            </div>

            {error && <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

            <button
              onClick={confirmBooking}
              disabled={booking || !name || !phone}
              className="clay-btn flex w-full items-center justify-center gap-2 rounded-2xl px-6 py-3 font-semibold"
            >
              {booking ? <Loader2 size={18} className="animate-spin" /> : <CircleCheck size={18} />}
              {booking ? "Confirming..." : "Confirm Booking"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

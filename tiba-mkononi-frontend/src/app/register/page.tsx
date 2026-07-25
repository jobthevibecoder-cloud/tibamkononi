"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Building2, ChevronLeft, ChevronRight, CircleCheck, MapPin, Plus, Trash2 } from "lucide-react";
import { apiPost } from "@/lib/api";

const STEPS = ["Basic Info", "Infrastructure", "Stock & Suppliers", "Admin Account & Staff"];

const FACILITY_TYPES = ["PHC", "CHC", "DISTRICT_HOSPITAL", "PRIVATE_CLINIC"];

const SUB_COUNTIES = [
  { id: "changamwe", name: "Changamwe" },
  { id: "jomvu", name: "Jomvu" },
  { id: "kisauni", name: "Kisauni" },
  { id: "likoni", name: "Likoni" },
  { id: "mvita", name: "Mvita" },
  { id: "nyali", name: "Nyali" },
];

const WARD_TYPES = ["GENERAL", "MATERNITY", "PAEDIATRIC", "ICU", "ISOLATION", "PRIVATE"];

const AMENITY_OPTIONS = [
  "Operating Theatre",
  "Laboratory",
  "Pharmacy",
  "X-Ray",
  "MRI",
  "Ultrasound",
  "Maternity Ward",
  "ICU",
  "Blood Bank",
  "Ambulance Bay",
  "Mortuary",
];

const UNIT_OPTIONS = ["bottles", "tablets", "doses", "vials", "sachets", "boxes", "ampoules"];
const STAFF_ROLES = ["Doctor", "Nurse", "Pharmacist", "Admin"];

type FormState = {
  name: string;
  license_number: string;
  type: string;
  county_id: string;
  sub_county_id: string;
  physical_address: string;
  phone: string;
  email: string;
  director_name: string;
  director_email: string;
  director_phone: string;
  director_password: string;
};

type Ward = { name: string; type: string; total_beds: string };
type Building = { name: string; floors: string; wards: Ward[] };
type InventoryRow = { medicine: string; quantity: string; unit: string; minimum_threshold: string };
type SupplierRow = { name: string; contact: string; supplies: string };
type StaffRow = { name: string; email: string; role: string };

const INITIAL: FormState = {
  name: "",
  license_number: "",
  type: FACILITY_TYPES[2],
  county_id: "mombasa",
  sub_county_id: SUB_COUNTIES[0].id,
  physical_address: "",
  phone: "",
  email: "",
  director_name: "",
  director_email: "",
  director_phone: "",
  director_password: "",
};

const EMPTY_WARD = (): Ward => ({ name: "", type: WARD_TYPES[0], total_beds: "" });
const EMPTY_BUILDING = (): Building => ({ name: "", floors: "1", wards: [EMPTY_WARD()] });
const EMPTY_INVENTORY = (): InventoryRow => ({ medicine: "", quantity: "", unit: UNIT_OPTIONS[0], minimum_threshold: "" });
const EMPTY_SUPPLIER = (): SupplierRow => ({ name: "", contact: "", supplies: "" });
const EMPTY_STAFF = (): StaffRow => ({ name: "", email: "", role: STAFF_ROLES[0] });

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<FormState>(INITIAL);
  const [buildings, setBuildings] = useState<Building[]>([EMPTY_BUILDING()]);
  const [amenities, setAmenities] = useState<string[]>([]);
  const [inventory, setInventory] = useState<InventoryRow[]>([EMPTY_INVENTORY()]);
  const [suppliers, setSuppliers] = useState<SupplierRow[]>([EMPTY_SUPPLIER()]);
  const [staff, setStaff] = useState<StaffRow[]>([EMPTY_STAFF()]);
  const [kmpdcConfirmed, setKmpdcConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [locating, setLocating] = useState(false);
  const [coords, setCoords] = useState<{ latitude: string; longitude: string }>({ latitude: "", longitude: "" });

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function useCurrentLocation() {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({ latitude: pos.coords.latitude.toFixed(6), longitude: pos.coords.longitude.toFixed(6) });
        setLocating(false);
      },
      () => setLocating(false),
      { timeout: 5000 }
    );
  }

  function addBuilding() {
    setBuildings((b) => [...b, EMPTY_BUILDING()]);
  }
  function removeBuilding(i: number) {
    setBuildings((b) => b.filter((_, idx) => idx !== i));
  }
  function updateBuilding(i: number, field: "name" | "floors", value: string) {
    setBuildings((b) => b.map((bld, idx) => (idx === i ? { ...bld, [field]: value } : bld)));
  }
  function addWard(bIdx: number) {
    setBuildings((b) => b.map((bld, idx) => (idx === bIdx ? { ...bld, wards: [...bld.wards, EMPTY_WARD()] } : bld)));
  }
  function removeWard(bIdx: number, wIdx: number) {
    setBuildings((b) => b.map((bld, idx) => (idx === bIdx ? { ...bld, wards: bld.wards.filter((_, i) => i !== wIdx) } : bld)));
  }
  function updateWard(bIdx: number, wIdx: number, field: keyof Ward, value: string) {
    setBuildings((b) =>
      b.map((bld, idx) =>
        idx === bIdx ? { ...bld, wards: bld.wards.map((w, i) => (i === wIdx ? { ...w, [field]: value } : w)) } : bld
      )
    );
  }
  function toggleAmenity(a: string) {
    setAmenities((list) => (list.includes(a) ? list.filter((x) => x !== a) : [...list, a]));
  }

  function addInventory() {
    setInventory((list) => [...list, EMPTY_INVENTORY()]);
  }
  function removeInventory(i: number) {
    setInventory((list) => list.filter((_, idx) => idx !== i));
  }
  function updateInventory(i: number, field: keyof InventoryRow, value: string) {
    setInventory((list) => list.map((row, idx) => (idx === i ? { ...row, [field]: value } : row)));
  }

  function addSupplier() {
    setSuppliers((list) => [...list, EMPTY_SUPPLIER()]);
  }
  function removeSupplier(i: number) {
    setSuppliers((list) => list.filter((_, idx) => idx !== i));
  }
  function updateSupplier(i: number, field: keyof SupplierRow, value: string) {
    setSuppliers((list) => list.map((row, idx) => (idx === i ? { ...row, [field]: value } : row)));
  }

  function addStaff() {
    setStaff((list) => [...list, EMPTY_STAFF()]);
  }
  function removeStaff(i: number) {
    setStaff((list) => list.filter((_, idx) => idx !== i));
  }
  function updateStaff(i: number, field: keyof StaffRow, value: string) {
    setStaff((list) => list.map((row, idx) => (idx === i ? { ...row, [field]: value } : row)));
  }

  async function submit() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost("/v1/hospitals/register", {
        name: form.name,
        license_number: form.license_number,
        type: form.type,
        county_id: form.county_id,
        sub_county_id: form.sub_county_id,
        physical_address: form.physical_address,
        latitude: coords.latitude ? Number(coords.latitude) : undefined,
        longitude: coords.longitude ? Number(coords.longitude) : undefined,
        phone: form.phone,
        email: form.email,
        director_name: form.director_name,
        director_email: form.director_email,
        director_phone: form.director_phone,
        buildings: buildings.map((b) => ({
          name: b.name,
          floors: Number(b.floors) || 0,
          wards: b.wards.map((w) => ({ name: w.name, type: w.type, total_beds: Number(w.total_beds) || 0 })),
        })),
        amenities,
      });

      const bedsTotal = buildings.reduce(
        (sum, b) => sum + b.wards.reduce((wSum, w) => wSum + (Number(w.total_beds) || 0), 0),
        0
      );

      sessionStorage.setItem(
        "tiba_registration",
        JSON.stringify({
          hospital_id: data?.hospital_id,
          slug: data?.slug,
          status: data?.status ?? "PENDING",
          name: form.name,
          physical_address: form.physical_address,
          license_number: form.license_number,
          type: form.type,
          director_name: form.director_name,
          buildings_count: buildings.length,
          beds_total: bedsTotal,
          amenities,
        })
      );

      router.push("/register/success");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="clay-card-flat flex h-12 w-12 items-center justify-center rounded-2xl text-amber-900">
          <Building2 size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-stone-900">Register Your Hospital</h1>
          <p className="text-sm text-stone-500">Tell us about your facility - it will go live after county approval.</p>
        </div>
      </div>

      <div className="clay-card space-y-6 p-6">
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-medium text-stone-500">
            {STEPS.map((s, i) => (
              <span key={s} className={i <= step ? "text-amber-900" : ""}>{s}</span>
            ))}
          </div>
          <div className="clay-progress-track h-2.5 w-full">
            <div className="clay-progress-fill h-full transition-all" style={{ width: `${((step + 1) / STEPS.length) * 100}%` }} />
          </div>
        </div>

        {step === 0 && (
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Hospital Name" value={form.name} onChange={(v) => update("name", v)} />
            <Field label="License Number" value={form.license_number} onChange={(v) => update("license_number", v)} />
            <SelectField label="Type" value={form.type} onChange={(v) => update("type", v)} options={FACILITY_TYPES.map((t) => ({ value: t, label: t.split("_").join(" ") }))} />
            <SelectField label="Sub-County" value={form.sub_county_id} onChange={(v) => update("sub_county_id", v)} options={SUB_COUNTIES.map((s) => ({ value: s.id, label: s.name }))} />
            <Field label="Phone" value={form.phone} onChange={(v) => update("phone", v)} />
            <Field label="Email" value={form.email} onChange={(v) => update("email", v)} type="email" />
            <div className="sm:col-span-2">
              <Field label="Physical Address" value={form.physical_address} onChange={(v) => update("physical_address", v)} />
            </div>
            <div className="clay-card-flat flex items-center justify-between gap-3 rounded-2xl px-4 py-3 sm:col-span-2">
              <span className="text-sm font-medium text-stone-600">Facility Location (optional)</span>
              <button onClick={useCurrentLocation} disabled={locating} className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs">
                {locating ? <Loader2 size={14} className="animate-spin" /> : <MapPin size={14} />} Use Current Location
              </button>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            {buildings.map((building, bIdx) => (
              <div key={bIdx} className="clay-card-flat space-y-3 rounded-2xl p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-stone-800">Building {bIdx + 1}</span>
                  {buildings.length > 1 && (
                    <button onClick={() => removeBuilding(bIdx)} className="text-stone-400 hover:text-red-600">
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Building Name" value={building.name} onChange={(v) => updateBuilding(bIdx, "name", v)} />
                  <Field label="Floors" value={building.floors} onChange={(v) => updateBuilding(bIdx, "floors", v)} type="number" />
                </div>
                <div className="space-y-2 pl-2">
                  <span className="text-xs font-semibold text-stone-500">Wards</span>
                  {building.wards.map((ward, wIdx) => (
                    <div key={wIdx} className="flex flex-wrap items-end gap-2 rounded-xl bg-white/60 p-3">
                      <div className="min-w-[140px] flex-1">
                        <Field label="Ward Name" value={ward.name} onChange={(v) => updateWard(bIdx, wIdx, "name", v)} />
                      </div>
                      <div className="min-w-[120px] flex-1">
                        <SelectField label="Type" value={ward.type} onChange={(v) => updateWard(bIdx, wIdx, "type", v)} options={WARD_TYPES.map((t) => ({ value: t, label: t }))} />
                      </div>
                      <div className="w-24">
                        <Field label="Beds" value={ward.total_beds} onChange={(v) => updateWard(bIdx, wIdx, "total_beds", v)} type="number" />
                      </div>
                      {building.wards.length > 1 && (
                        <button onClick={() => removeWard(bIdx, wIdx)} className="mb-2.5 text-stone-400 hover:text-red-600">
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  ))}
                  <button onClick={() => addWard(bIdx)} className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs">
                    <Plus size={14} /> Add Ward
                  </button>
                </div>
              </div>
            ))}
            <button onClick={addBuilding} className="clay-btn flex items-center gap-1 rounded-xl px-4 py-2 text-sm">
              <Plus size={16} /> Add Building
            </button>

            <div className="space-y-2">
              <span className="text-sm font-medium text-stone-600">Amenities</span>
              <div className="flex flex-wrap gap-2">
                {AMENITY_OPTIONS.map((a) => (
                  <button
                    key={a}
                    onClick={() => toggleAmenity(a)}
                    className={`clay-pill px-4 py-2 text-sm font-medium ${amenities.includes(a) ? "tab-active" : "clay-card-flat text-stone-600"}`}
                  >
                    {a}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <p className="rounded-xl bg-amber-50 px-4 py-2.5 text-xs text-amber-800">
              These get added after your hospital is approved and you log in - saved here for reference but not sent yet.
            </p>
            <div className="space-y-3">
              <span className="text-sm font-medium text-stone-600">Initial Inventory</span>
              {inventory.map((row, i) => (
                <div key={i} className="flex flex-wrap items-end gap-2 rounded-xl bg-stone-50 p-3">
                  <div className="min-w-[160px] flex-1">
                    <Field label="Medicine" value={row.medicine} onChange={(v) => updateInventory(i, "medicine", v)} />
                  </div>
                  <div className="w-24">
                    <Field label="Quantity" value={row.quantity} onChange={(v) => updateInventory(i, "quantity", v)} type="number" />
                  </div>
                  <div className="w-32">
                    <SelectField label="Unit" value={row.unit} onChange={(v) => updateInventory(i, "unit", v)} options={UNIT_OPTIONS.map((u) => ({ value: u, label: u }))} />
                  </div>
                  <div className="w-28">
                    <Field label="Min. Threshold" value={row.minimum_threshold} onChange={(v) => updateInventory(i, "minimum_threshold", v)} type="number" />
                  </div>
                  {inventory.length > 1 && (
                    <button onClick={() => removeInventory(i)} className="mb-2.5 text-stone-400 hover:text-red-600">
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              ))}
              <button onClick={addInventory} className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs">
                <Plus size={14} /> Add Medicine
              </button>
            </div>

            <div className="space-y-3">
              <span className="text-sm font-medium text-stone-600">Suppliers</span>
              {suppliers.map((row, i) => (
                <div key={i} className="flex flex-wrap items-end gap-2 rounded-xl bg-stone-50 p-3">
                  <div className="min-w-[140px] flex-1">
                    <Field label="Name" value={row.name} onChange={(v) => updateSupplier(i, "name", v)} />
                  </div>
                  <div className="min-w-[140px] flex-1">
                    <Field label="Contact" value={row.contact} onChange={(v) => updateSupplier(i, "contact", v)} />
                  </div>
                  <div className="min-w-[160px] flex-1">
                    <Field label="Supplies" value={row.supplies} onChange={(v) => updateSupplier(i, "supplies", v)} />
                  </div>
                  {suppliers.length > 1 && (
                    <button onClick={() => removeSupplier(i)} className="mb-2.5 text-stone-400 hover:text-red-600">
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              ))}
              <button onClick={addSupplier} className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs">
                <Plus size={14} /> Add Supplier
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <div className="space-y-4">
              <span className="text-sm font-bold text-stone-800">Director Account (Full Access)</span>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Director Name" value={form.director_name} onChange={(v) => update("director_name", v)} />
                <Field label="Director Phone" value={form.director_phone} onChange={(v) => update("director_phone", v)} />
                <Field label="Director Email" value={form.director_email} onChange={(v) => update("director_email", v)} type="email" />
                <div>
                  <Field label="Password" value={form.director_password} onChange={(v) => update("director_password", v)} type="password" />
                  <p className="mt-1 text-xs text-stone-400">Not sent yet - director accounts are created separately for now.</p>
                </div>
              </div>
            </div>

            <div className="space-y-3 border-t border-stone-200 pt-4">
              <span className="text-sm font-bold text-stone-800">Staff Accounts</span>
              <p className="rounded-xl bg-amber-50 px-4 py-2.5 text-xs text-amber-800">
                Saved for reference only - staff accounts get added after approval.
              </p>
              {staff.map((row, i) => (
                <div key={i} className="flex flex-wrap items-end gap-2 rounded-xl bg-stone-50 p-3">
                  <div className="min-w-[140px] flex-1">
                    <Field label="Name" value={row.name} onChange={(v) => updateStaff(i, "name", v)} />
                  </div>
                  <div className="min-w-[160px] flex-1">
                    <Field label="Email" value={row.email} onChange={(v) => updateStaff(i, "email", v)} type="email" />
                  </div>
                  <div className="w-36">
                    <SelectField label="Role" value={row.role} onChange={(v) => updateStaff(i, "role", v)} options={STAFF_ROLES.map((r) => ({ value: r, label: r }))} />
                  </div>
                  {staff.length > 1 && (
                    <button onClick={() => removeStaff(i)} className="mb-2.5 text-stone-400 hover:text-red-600">
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              ))}
              <button onClick={addStaff} className="clay-btn-secondary flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs">
                <Plus size={14} /> Add Staff Account
              </button>
            </div>

            <label className="clay-card-flat flex items-start gap-3 rounded-2xl p-4">
              <input type="checkbox" checked={kmpdcConfirmed} onChange={(e) => setKmpdcConfirmed(e.target.checked)} className="mt-1 h-4 w-4" />
              <span className="text-sm text-stone-600">I confirm this hospital is licensed by KMPDC.</span>
            </label>
          </div>
        )}

        {error && <div className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

        <div className="flex justify-between pt-2">
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="clay-btn-secondary flex items-center gap-1 rounded-xl px-4 py-2 text-sm disabled:opacity-40"
          >
            <ChevronLeft size={16} /> Back
          </button>
          {step < STEPS.length - 1 ? (
            <button onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))} className="clay-btn flex items-center gap-1 rounded-xl px-4 py-2 text-sm">
              Next <ChevronRight size={16} />
            </button>
          ) : (
            <button
              onClick={submit}
              disabled={loading || !kmpdcConfirmed}
              className="clay-btn flex items-center gap-2 rounded-xl px-5 py-2 text-sm disabled:opacity-40"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : <CircleCheck size={16} />}
              {loading ? "Submitting..." : "Submit Registration"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, type = "text" }: { label: string; value: string; onChange: (v: string) => void; type?: string }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm font-medium text-stone-600">{label}</span>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} className="clay-input w-full px-4 py-2.5" />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm font-medium text-stone-600">{label}</span>
      <select className="clay-input w-full px-4 py-2.5" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </label>
  );
}

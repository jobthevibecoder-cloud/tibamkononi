"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Building2, LogIn, ShieldCheck, Siren, Stethoscope, ClipboardList, Megaphone } from "lucide-react";
import { apiGet } from "@/lib/api";

type Stats = { hospitals: number; totalBeds: number; bedsAvailable: number; criticalAlerts: number };

const TOOLS = [
  { href: "/emergency", icon: Siren, title: "Emergency Response", desc: "Describe an emergency and get routed to the nearest capable hospital instantly." },
  { href: "/triage", icon: Stethoscope, title: "AI Self-Diagnosis", desc: "Describe symptoms in Swahili or English and get a triage level from Gemma 4." },
  { href: "/appointments", icon: ClipboardList, title: "Appointments", desc: "Book a slot at any partner hospital in under a minute." },
  { href: "/announcements", icon: Megaphone, title: "County Announcements", desc: "Stay current on medicine deliveries, funding and health alerts." },
];

export default function LandingPage() {
  const [stats, setStats] = useState<Stats>({ hospitals: 0, totalBeds: 0, bedsAvailable: 0, criticalAlerts: 0 });

  useEffect(() => {
    apiGet("/v1/county/dashboard")
      .then((data) => {
        setStats({
          hospitals: data?.total_hospitals ?? 0,
          totalBeds: data?.total_beds ?? 0,
          bedsAvailable: data?.beds_available ?? 0,
          criticalAlerts: data?.critical_alerts ?? 0,
        });
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-16">
      <section className="clay-card flex flex-col items-center gap-6 px-8 py-16 text-center">
        <h1 className="max-w-2xl text-4xl font-extrabold text-stone-900 sm:text-5xl">Tiba Mkononi</h1>
        <p className="max-w-xl text-lg text-stone-500">
          AI-powered hospital management for Mombasa County. Track stock, predict shortages, and redistribute
          resources intelligently.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link href="/register" className="clay-btn flex items-center gap-2 rounded-2xl px-6 py-3 font-semibold">
            <Building2 size={18} /> Register Your Hospital
          </Link>
          <Link href="/login" className="clay-btn-secondary flex items-center gap-2 rounded-2xl px-6 py-3 font-semibold">
            <LogIn size={18} /> Hospital Login
          </Link>
        </div>
        <div className="pt-2 text-sm text-stone-500">
          Are you a County Official?{" "}
          <Link href="/county-login" className="inline-flex items-center gap-1 font-semibold text-amber-800 underline-offset-2 hover:underline">
            <ShieldCheck size={14} /> County Director Login
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Hospitals", value: stats.hospitals },
          { label: "Total Beds", value: stats.totalBeds },
          { label: "Beds Available", value: stats.bedsAvailable },
          { label: "Critical Alerts", value: stats.criticalAlerts },
        ].map((s) => (
          <div key={s.label} className="clay-card px-4 py-6 text-center">
            <div className="text-3xl font-extrabold text-amber-900">{s.value}</div>
            <div className="mt-1 text-sm text-stone-500">{s.label}</div>
          </div>
        ))}
      </section>

      <section className="space-y-5">
        <h2 className="text-center text-xl font-bold text-stone-900">Community Health Tools</h2>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {TOOLS.map(({ href, icon: Icon, title, desc }) => (
            <Link key={href} href={href} className="clay-card flex flex-col gap-3 px-6 py-6 transition-transform hover:-translate-y-1">
              <div className="clay-card-flat flex h-12 w-12 items-center justify-center rounded-2xl text-amber-900">
                <Icon size={22} />
              </div>
              <h3 className="text-base font-bold text-stone-900">{title}</h3>
              <p className="text-sm text-stone-500">{desc}</p>
            </Link>
          ))}
        </div>
      </section>

      <footer className="pb-8 text-center text-sm text-stone-500">
        Built with Gemma 4 - GDG Pwani Hackathon 2026
      </footer>
    </div>
  );
}

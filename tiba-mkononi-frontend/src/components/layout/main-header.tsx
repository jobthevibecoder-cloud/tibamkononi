"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Siren, Stethoscope, ClipboardList, Megaphone, HeartPulse, LogIn } from "lucide-react";

const TABS = [
  { href: "/emergency", label: "Emergency", icon: Siren },
  { href: "/triage", label: "Self-Diagnose", icon: Stethoscope },
  { href: "/appointments", label: "Appointments", icon: ClipboardList },
  { href: "/announcements", label: "Announcements", icon: Megaphone },
];

export default function MainHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-white/40 bg-stone-100/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="flex items-center gap-2">
          <div className="clay-card-flat flex h-9 w-9 items-center justify-center rounded-2xl text-amber-900">
            <HeartPulse size={18} />
          </div>
          <span className="text-lg font-bold text-amber-900">Tiba Mkononi</span>
        </Link>

        <nav className="clay-card-flat flex items-center gap-1 rounded-2xl p-1.5">
          {TABS.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition-all ${
                  active ? "tab-active" : "tab-inactive"
                }`}
              >
                <Icon size={18} />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}
        </nav>

        <Link href="/login" className="clay-btn-secondary flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold">
          <LogIn size={16} />
          <span className="hidden sm:inline">Hospital Login</span>
        </Link>
      </div>
    </header>
  );
}

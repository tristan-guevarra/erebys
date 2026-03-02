"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import {
  LayoutDashboard, Building2, TrendingUp, Users, Activity, Settings, LogOut, ChevronDown,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/platform",           label: "Overview",  icon: LayoutDashboard },
  { href: "/platform/academies", label: "Academies", icon: Building2       },
  { href: "/platform/revenue",   label: "Revenue",   icon: TrendingUp      },
  { href: "/platform/users",     label: "Users",     icon: Users           },
  { href: "/platform/health",    label: "Health",    icon: Activity        },
  { href: "/platform/settings",  label: "Settings",  icon: Settings        },
];

export default function PlatformLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) setUserMenuOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  useEffect(() => {
    if (!isLoading && !user) router.push("/login");
    else if (!isLoading && user && !user.is_superadmin) router.push("/dashboard");
  }, [user, isLoading, router]);

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-6 h-6 rounded-full border-2 border-t-transparent animate-spin"
           style={{ borderColor: "var(--accent-cyan)", borderTopColor: "transparent" }} />
    </div>
  );

  if (!user || !user.is_superadmin) return null;

  const isActive = (href: string) => {
    if (href === "/platform") return pathname === "/platform";
    return pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* fixed top header */}
      <header className="fixed top-0 inset-x-0 z-40 h-14 border-b border-[var(--border-subtle)]"
              style={{ background: "rgba(11,11,17,0.92)", backdropFilter: "blur(12px)" }}>
        <div className="flex items-center h-full px-4 gap-4 max-w-[1600px] mx-auto">
          {/* logo */}
          <Link href="/platform" className="flex items-center gap-2.5 shrink-0">
            <Image src="/logo-icon.png" alt="Erebys" width={32} height={32} className="h-7 w-7 object-contain" />
            <span className="font-display font-bold text-[15px] tracking-tight hidden sm:block"
                  style={{ color: "var(--accent-cyan)" }}>
              Platform
            </span>
          </Link>

          {/* superadmin badge */}
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-bold tracking-widest shrink-0"
                style={{ background: "rgba(6,182,212,0.12)", color: "var(--accent-cyan)", border: "1px solid rgba(6,182,212,0.20)" }}>
            SUPERADMIN
          </span>

          {/* vertical divider */}
          <div className="h-5 w-px bg-[var(--border-subtle)] shrink-0" />

          {/* nav items */}
          <nav className="flex items-center gap-0.5 flex-1 overflow-x-auto scrollbar-none">
            {NAV_ITEMS.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="nav-item"
                  style={active ? {
                    background: "rgba(6,182,212,0.10)",
                    color: "var(--accent-cyan)",
                  } : {}}
                >
                  <item.icon className="w-3.5 h-3.5 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* right controls */}
          <div className="flex items-center gap-2 shrink-0">
            {/* user avatar + dropdown */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg
                           hover:bg-white/[0.05] transition-colors"
              >
                <div className="w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold text-white"
                     style={{ background: "rgba(6,182,212,0.25)", border: "1px solid rgba(6,182,212,0.25)" }}>
                  {user.full_name.split(" ").map((n: string) => n[0]).join("").slice(0, 2)}
                </div>
                <span className="text-sm text-[var(--text-secondary)] max-w-[120px] truncate hidden sm:block">
                  {user.full_name}
                </span>
                <ChevronDown className={`w-3 h-3 text-[var(--text-muted)] transition-transform ${userMenuOpen ? "rotate-180" : ""}`} />
              </button>
              {userMenuOpen && (
                <div className="absolute right-0 top-full mt-1.5 w-52 rounded-xl
                                bg-[var(--bg-card)] border border-[var(--border-subtle)]
                                shadow-xl shadow-black/40 z-50 overflow-hidden">
                  <div className="px-3 py-2.5 border-b border-[var(--border-subtle)]">
                    <p className="text-xs font-medium text-[var(--text-primary)] truncate">{user.full_name}</p>
                    <p className="text-xs text-[var(--text-muted)] truncate mt-0.5">{user.email}</p>
                    <p className="text-xs font-mono mt-0.5" style={{ color: "var(--accent-cyan)" }}>Superadmin</p>
                  </div>
                  <div className="py-1">
                    <button
                      onClick={logout}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--text-secondary)]
                                 hover:text-accent-rose hover:bg-white/5 transition-colors"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* page content */}
      <main className="pt-14">
        <div className="max-w-[1400px] mx-auto px-4 lg:px-6 py-6">
          {children}
        </div>
      </main>
    </div>
  );
}

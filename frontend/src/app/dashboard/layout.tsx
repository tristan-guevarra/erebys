"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { useQueryClient } from "@tanstack/react-query";
import {
  LayoutDashboard, Calendar, DollarSign, Users, Briefcase,
  ClipboardList, FlaskConical, Lightbulb, Settings, LogOut,
  Zap, ChevronDown,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard",             label: "Overview",    icon: LayoutDashboard },
  { href: "/dashboard/events",      label: "Events",      icon: Calendar        },
  { href: "/dashboard/pricing",     label: "Pricing",     icon: DollarSign      },
  { href: "/dashboard/athletes",    label: "Athletes",    icon: Users           },
  { href: "/dashboard/coaches",     label: "Coaches",     icon: Briefcase       },
  { href: "/dashboard/evaluations", label: "Evaluations", icon: ClipboardList   },
  { href: "/dashboard/experiments", label: "Experiments", icon: FlaskConical    },
  { href: "/dashboard/insights",    label: "Insights",    icon: Lightbulb       },
  { href: "/dashboard/settings",    label: "Settings",    icon: Settings        },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, currentOrg, isLoading, logout, selectOrg } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const queryClient = useQueryClient();

  const [orgDropdownOpen, setOrgDropdownOpen] = useState(false);
  const orgDropdownRef = useRef<HTMLDivElement>(null);

  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (orgDropdownRef.current && !orgDropdownRef.current.contains(e.target as Node)) setOrgDropdownOpen(false);
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) setUserMenuOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSelectOrg = (orgId: string) => {
    selectOrg(orgId);
    queryClient.invalidateQueries();
    setOrgDropdownOpen(false);
  };

  useEffect(() => {
    if (!isLoading && !user) router.push("/login");
    else if (!isLoading && user?.is_superadmin) router.push("/platform");
  }, [user, isLoading, router]);

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-6 h-6 rounded-full border-2 border-erebys-600 border-t-transparent animate-spin" />
    </div>
  );

  if (!user) return null;

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      {/* fixed top header */}
      <header className="fixed top-0 inset-x-0 z-40 h-14 border-b border-[var(--border-subtle)] bg-[var(--bg-primary)]/95 backdrop-blur-sm">
        <div className="flex items-center h-full px-4 gap-4 max-w-[1600px] mx-auto">
          {/* logo */}
          <Link href="/dashboard" className="flex items-center gap-2 shrink-0">
            <div className="w-7 h-7 rounded-lg bg-erebys-600 flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-display font-bold text-[15px] tracking-tight text-[var(--text-primary)]">
              Erebys
            </span>
          </Link>

          {/* vertical divider */}
          <div className="h-5 w-px bg-[var(--border-subtle)] shrink-0" />

          {/* nav items — horizontal scroll on small screens */}
          <nav className="flex items-center gap-0.5 flex-1 overflow-x-auto scrollbar-none">
            {NAV_ITEMS.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`nav-item ${active ? "nav-item-active" : ""}`}
                >
                  <item.icon className="w-3.5 h-3.5 shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* right controls */}
          <div className="flex items-center gap-2 shrink-0">
            {/* org selector */}
            {currentOrg && user?.org_roles && user.org_roles.length > 0 && (
              <div className="relative" ref={orgDropdownRef}>
                <button
                  onClick={() => setOrgDropdownOpen(!orgDropdownOpen)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                             bg-[var(--bg-card)] border border-[var(--border-subtle)]
                             hover:border-[var(--border-active)] text-sm font-medium
                             text-[var(--text-primary)] transition-colors max-w-[160px]"
                >
                  <span className="truncate">{currentOrg.organization_name || "Org"}</span>
                  <ChevronDown className={`w-3 h-3 text-[var(--text-muted)] shrink-0 transition-transform ${orgDropdownOpen ? "rotate-180" : ""}`} />
                </button>
                {orgDropdownOpen && user.org_roles.length > 1 && (
                  <div className="absolute right-0 top-full mt-1.5 w-52 rounded-xl
                                  bg-[var(--bg-card)] border border-[var(--border-subtle)]
                                  shadow-xl shadow-black/40 z-50 overflow-hidden py-1">
                    {user.org_roles.map((role) => (
                      <button
                        key={role.organization_id}
                        onClick={() => handleSelectOrg(role.organization_id)}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-white/5 transition-colors flex items-center justify-between ${
                          role.organization_id === currentOrg.organization_id
                            ? "text-erebys-400"
                            : "text-[var(--text-secondary)]"
                        }`}
                      >
                        <span className="truncate">{role.organization_name || role.organization_id}</span>
                        {role.organization_id === currentOrg.organization_id && (
                          <span className="w-1.5 h-1.5 rounded-full bg-erebys-400 shrink-0 ml-2" />
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* user avatar + dropdown */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg
                           hover:bg-white/[0.05] transition-colors"
              >
                <div className="w-6 h-6 rounded-full bg-erebys-800 border border-erebys-600/30
                                flex items-center justify-center text-[10px] font-bold text-erebys-300">
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
                    <p className="text-xs text-[var(--text-muted)] capitalize mt-0.5">{currentOrg?.role}</p>
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

      {/* page content — offset for fixed header */}
      <main className="pt-14">
        <div className="max-w-[1400px] mx-auto px-4 lg:px-6 py-6">
          {children}
        </div>
      </main>
    </div>
  );
}

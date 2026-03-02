"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { PageLoader, PageHeader, Card } from "@/components/ui/shared";
import { usePlatformUsers, usePatchPlatformUser } from "@/hooks/use-platform";
import type { PlatformUser } from "@/types";

export default function UsersPage() {
  const { data, isLoading } = usePlatformUsers();
  const patchUser = usePatchPlatformUser();
  const [search, setSearch] = useState("");

  if (isLoading) return <PageLoader />;

  const users = (data as PlatformUser[] | undefined) || [];

  const filtered = users.filter(
    (u) =>
      u.full_name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  );

  const handleToggleActive = (user: PlatformUser) => {
    patchUser.mutate({ userId: user.id, data: { is_active: !user.is_active } });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Users"
        description={`${users.length} users across all academies`}
      />

      {/* search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by name or email…"
          className="input-field pl-9 w-full"
        />
      </div>

      <Card noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-wider text-[var(--text-muted)] border-b border-[var(--border-subtle)]">
                <th className="px-5 py-3 text-left font-medium">Name</th>
                <th className="px-5 py-3 text-left font-medium">Email</th>
                <th className="px-5 py-3 text-center font-medium">
                  Superadmin
                </th>
                <th className="px-5 py-3 text-center font-medium">Active</th>
                <th className="px-5 py-3 text-left font-medium">
                  Organizations
                </th>
                <th className="px-5 py-3 text-center font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-subtle)]">
              {filtered.map((user) => (
                <tr
                  key={user.id}
                  className="hover:bg-[var(--bg-card)]/40 transition-colors"
                >
                  {/* name */}
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2.5">
                      <div
                        className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0"
                        style={{ background: "rgba(6,182,212,0.25)" }}
                      >
                        {user.full_name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")
                          .slice(0, 2)}
                      </div>
                      <span className="font-medium text-[var(--text-primary)]">
                        {user.full_name}
                      </span>
                    </div>
                  </td>

                  {/* email */}
                  <td className="px-5 py-3 text-[var(--text-secondary)] font-mono text-xs">
                    {user.email}
                  </td>

                  {/* superadmin */}
                  <td className="px-5 py-3 text-center">
                    {user.is_superadmin ? (
                      <span
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                        style={{
                          background: "rgba(6,182,212,0.12)",
                          color: "var(--accent-cyan)",
                          border: "1px solid rgba(6,182,212,0.25)",
                        }}
                      >
                        Yes
                      </span>
                    ) : (
                      <span className="text-[var(--text-muted)]">—</span>
                    )}
                  </td>

                  {/* active toggle */}
                  <td className="px-5 py-3 text-center">
                    <button
                      onClick={() => handleToggleActive(user)}
                      disabled={patchUser.isPending}
                      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none disabled:opacity-50 ${
                        user.is_active
                          ? "bg-[var(--accent-emerald)]"
                          : "bg-[var(--bg-secondary)]"
                      }`}
                      title={user.is_active ? "Deactivate user" : "Activate user"}
                    >
                      <span
                        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                          user.is_active ? "translate-x-4.5" : "translate-x-0.5"
                        }`}
                      />
                    </button>
                  </td>

                  {/* organizations */}
                  <td className="px-5 py-3">
                    <span className="text-xs text-[var(--text-secondary)]">
                      {user.orgs && user.orgs.length > 0
                        ? user.orgs.map((o) => o.org_name).join(", ")
                        : "—"}
                    </span>
                  </td>

                  {/* actions */}
                  <td className="px-5 py-3 text-center">
                    <button
                      onClick={() => handleToggleActive(user)}
                      disabled={patchUser.isPending}
                      className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--border-active)] transition-colors disabled:opacity-50"
                    >
                      {user.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </td>
                </tr>
              ))}

              {filtered.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-5 py-10 text-center text-[var(--text-muted)]"
                  >
                    {search ? "No users match your search." : "No users found."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Image from "next/image";
import { Mail, Lock, ArrowRight, Shield, Users } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);
  const { login }               = useAuth();
  const router                  = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const loginUser = await login(email, password);
      router.push(loginUser.is_superadmin ? "/platform" : "/dashboard");
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Invalid credentials";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
         style={{ background: "var(--bg-primary)" }}>

      {/* background effects */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[700px] h-[500px]
                        bg-erebys-600/[0.06] rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 left-1/3 w-[400px] h-[300px]
                        bg-erebys-400/[0.04] rounded-full blur-[100px]" />
        <div className="absolute top-1/4 right-1/4 w-[300px] h-[300px]
                        bg-cyan-500/[0.03] rounded-full blur-[80px]" />
      </div>

      <div className="relative w-full max-w-[420px] animate-fade-in">
        {/* logo */}
        <div className="flex flex-col items-center mb-10">
          <Image
            src="/logo.png"
            alt="Erebys"
            width={400}
            height={120}
            className="h-[90px] w-auto mb-4"
            priority
          />
          <p className="text-sm text-[var(--text-muted)]">
            Intelligence Suite for Sports Academies
          </p>
        </div>

        {/* card */}
        <div className="rounded-2xl p-8 animate-slide-up"
             style={{
               background: "linear-gradient(135deg, rgba(22,22,31,0.9), rgba(22,22,31,0.95))",
               border: "1px solid rgba(255,255,255,0.06)",
               boxShadow: "0 24px 80px rgba(0,0,0,0.4), 0 0 60px rgba(132,98,194,0.04)",
             }}>
          <h2 className="font-display text-lg font-semibold mb-6 text-[var(--text-primary)]">
            Sign in to your account
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1.5">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-10"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg
                              bg-rose-500/8 border border-rose-500/15 text-accent-rose text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full justify-center py-2.5 mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* demo shortcuts */}
          <div className="mt-6 pt-5 border-t border-[var(--border-subtle)]">
            <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-widest text-center mb-3">Quick demo</p>
            <div className="grid grid-cols-2 gap-2">
              {[
                { role: "admin", label: "Admin", icon: Shield, email: "admin@erebys.io", pass: "admin123" },
                { role: "owner", label: "Owner", icon: Users, email: "owner@elite-soccer.com", pass: "password123" },
              ].map((demo) => (
                <button
                  key={demo.role}
                  onClick={() => { setEmail(demo.email); setPassword(demo.pass); }}
                  disabled={loading}
                  className="flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl
                             bg-white/[0.03] border border-[var(--border-subtle)]
                             hover:border-[var(--border-active)] hover:bg-white/[0.05]
                             text-xs text-[var(--text-secondary)] transition-all disabled:opacity-50"
                >
                  <demo.icon className="w-3.5 h-3.5 text-erebys-400" />
                  {demo.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Zap } from "lucide-react";

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

      {/* background glow blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px]
                        bg-erebys-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/4 w-[400px] h-[300px]
                        bg-cyan-500/4 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-[400px] animate-fade-in">
        {/* logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-erebys-600 flex items-center justify-center shadow-lg shadow-erebys-600/25">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <h1 className="font-display text-2xl font-bold tracking-tight text-[var(--text-primary)]">
              Erebys
            </h1>
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            Intelligence Suite for Sports Academies
          </p>
        </div>

        {/* card */}
        <div className="card-glass rounded-2xl p-7 animate-slide-up">
          <h2 className="font-display text-lg font-semibold mb-5 text-[var(--text-primary)]">
            Sign in
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••"
                required
              />
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
                  Signing in…
                </>
              ) : (
                "Sign in"
              )}
            </button>
          </form>

          <div className="mt-5 pt-4 border-t border-[var(--border-subtle)]">
            <p className="text-xs text-[var(--text-muted)] text-center">
              Demo:&nbsp;
              <span className="font-mono text-[var(--text-secondary)]">admin@erebys.io</span>
              &nbsp;/&nbsp;
              <span className="font-mono text-[var(--text-secondary)]">admin123</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

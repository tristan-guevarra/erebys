"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import { api } from "@/lib/api";
import type { User, OrgRole } from "@/types";

interface AuthContextType {
  user: User | null;
  currentOrg: OrgRole | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
  selectOrg: (orgId: string) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [currentOrg, setCurrentOrg] = useState<OrgRole | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // on page load, check if there's already a token saved and restore the session
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api
        .getMe()
        .then(({ data }) => {
          setUser(data);
          const orgId = localStorage.getItem("current_org_id");
          const org = data.org_roles?.find(
            (r: OrgRole) => r.organization_id === orgId
          );
          setCurrentOrg(org || data.org_roles?.[0] || null);
          if (!orgId && data.org_roles?.[0]) {
            localStorage.setItem(
              "current_org_id",
              data.org_roles[0].organization_id
            );
          }
        })
        .catch(() => {
          localStorage.clear();
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string): Promise<User> => {
    const { data } = await api.login(email, password);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);

    setUser(data.user);

    const firstOrg = data.user.org_roles?.[0];
    if (firstOrg) {
      localStorage.setItem("current_org_id", firstOrg.organization_id);
      setCurrentOrg(firstOrg);
    }
    return data.user;
  }, []);

  const logout = useCallback(() => {
    localStorage.clear();
    setUser(null);
    setCurrentOrg(null);
    window.location.href = "/login";
  }, []);

  const selectOrg = useCallback(
    (orgId: string) => {
      localStorage.setItem("current_org_id", orgId);
      const org = user?.org_roles?.find((r) => r.organization_id === orgId);
      if (org) setCurrentOrg(org);
    },
    [user]
  );

  return (
    <AuthContext.Provider
      value={{ user, currentOrg, isLoading, login, logout, selectOrg }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

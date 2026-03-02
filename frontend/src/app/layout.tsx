import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import { QueryProvider } from "@/lib/query-provider";
import { ToastProvider } from "@/lib/toast-context";
import "./globals.css";

export const metadata: Metadata = {
  title: "Erebys Intelligence Suite",
  description: "B2B analytics + dynamic pricing engine for sports academies",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-grid min-h-screen">
        <QueryProvider>
          <AuthProvider>
              <ToastProvider>
                {children}
              </ToastProvider>
            </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}

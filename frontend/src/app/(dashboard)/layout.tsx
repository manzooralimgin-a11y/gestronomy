"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getMe } from "@/lib/auth";
import { getDefaultDashboardRoute } from "@/lib/role-routing";
import { useAuthStore } from "@/stores/auth-store";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const setUser = useAuthStore((s) => s.setUser);
  const token = useAuthStore((s) => s.token);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!token) {
      router.replace("/login");
      return;
    }

    getMe()
      .then((user) => {
        setUser(user);
        if (pathname === "/") {
          const target = getDefaultDashboardRoute(user.role);
          if (target !== "/") {
            router.replace(target);
          }
        }
      })
      .catch(() => {
        router.replace("/login");
      });
  }, [token, setUser, router, pathname]);

  return (
    <div className="min-h-screen bg-background">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {/* md:ml-[260px] pushes content right on desktop; on mobile the sidebar overlays */}
      <div className="md:ml-[260px]">
        <Header onMenuToggle={() => setSidebarOpen((prev) => !prev)} />
        <main id="main-content" className="p-3 md:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

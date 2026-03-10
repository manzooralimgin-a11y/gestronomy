"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getMe } from "@/lib/auth";
import { getDefaultDashboardRoute } from "@/lib/role-routing";
import { useAuthStore } from "@/stores/auth-store";
import { useUIStore } from "@/stores/ui-store";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const setUser = useAuthStore((s) => s.setUser);
  const token = useAuthStore((s) => s.token);
  const sidebarCollapsed = useUIStore((s) => s.sidebarCollapsed);
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
    <div className="min-h-screen mesh-gradient">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {/* Dynamic margin based on sidebar state */}
      <div
        className={`transition-[margin-left] duration-300 ease-standard ${
          sidebarCollapsed ? "md:ml-[72px]" : "md:ml-[260px]"
        }`}
      >
        <Header onMenuToggle={() => setSidebarOpen((prev) => !prev)} />
        <main id="main-content" className="p-4 md:p-6 flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}

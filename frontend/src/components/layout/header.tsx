"use client";

import { usePathname, useRouter } from "next/navigation";
import { Bell, LogOut, Menu, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useDashboardStore } from "@/stores/dashboard-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CommandBar } from "@/components/layout/command-bar";
import { ModeToggle } from "@/components/ui/mode-toggle";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

function getBreadcrumbs(pathname: string | null) {
  if (!pathname) return [{ label: "Dashboard", href: "/" }];
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return [{ label: "Dashboard", href: "/" }];
  return [
    { label: "Dashboard", href: "/" },
    ...segments.map((segment, index) => ({
      label: segment
        .replace(/-/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase()),
      href: `/${segments.slice(0, index + 1).join("/")}`,
    })),
  ];
}

interface HeaderProps {
  onMenuToggle?: () => void;
}

export function Header({ onMenuToggle }: HeaderProps) {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clear);
  const alerts = useDashboardStore((s) => s.alerts);
  const unreadCount = alerts.filter((a) => !a.is_read).length;
  const breadcrumbs = getBreadcrumbs(pathname);

  const handleLogout = () => {
    clearAuth();
    router.push("/login");
  };

  return (
    <header className="flex h-14 md:h-16 items-center justify-between glass-header px-4 md:px-8 sticky top-0 z-30">
      <div className="flex items-center gap-3">
        {/* Hamburger — mobile only */}
        <button
          type="button"
          aria-label="Open navigation menu"
          onClick={onMenuToggle}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-foreground-muted hover:bg-[rgba(255,253,240,0.05)] hover:text-foreground transition-colors md:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Breadcrumbs */}
        <nav className="hidden sm:flex items-center gap-1 text-sm font-body">
          {breadcrumbs.map((crumb, index) => (
            <span key={crumb.href} className="flex items-center gap-1">
              {index > 0 && (
                <span className="text-foreground-dim mx-0.5">/</span>
              )}
              <span
                className={cn(
                  "transition-colors",
                  index === breadcrumbs.length - 1
                    ? "font-medium text-foreground"
                    : "text-foreground-dim hover:text-foreground-muted"
                )}
              >
                {crumb.label}
              </span>
            </span>
          ))}
        </nav>

        {/* Mobile title */}
        <span className="text-sm font-body font-semibold text-foreground sm:hidden">
          {breadcrumbs[breadcrumbs.length - 1]?.label || "Dashboard"}
        </span>
      </div>

      <div className="flex items-center gap-2 md:gap-3">
        {/* Command bar */}
        <div className="hidden md:block">
          <CommandBar />
        </div>

        {/* Theme toggle */}
        <ModeToggle />

        {/* Alert bell */}
        <Button
          variant="ghost"
          size="icon-sm"
          className="relative text-foreground-muted hover:text-foreground"
          aria-label="Open alerts"
          onClick={() => router.push("/alerts")}
        >
          <Bell className="h-[18px] w-[18px]" />
          {unreadCount > 0 && (
            <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-status-danger text-[9px] font-bold text-white ring-2 ring-background animate-pulse px-1">
              {unreadCount > 99 ? "99" : unreadCount}
            </span>
          )}
        </Button>

        {/* User menu */}
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <Button
              variant="ghost"
              className="flex items-center gap-2 px-2"
              aria-label="Open user menu"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(212,175,55,0.12)] border border-[rgba(212,175,55,0.2)] text-xs font-editorial font-semibold text-gold">
                {user?.full_name
                  ?.split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase() || <User className="h-3.5 w-3.5" />}
              </div>
              <span className="hidden text-sm font-body font-medium text-foreground/80 md:block">
                {user?.full_name || "User"}
              </span>
            </Button>
          </DropdownMenu.Trigger>

          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 min-w-[180px] glass-modal p-1.5 animate-scale-bounce"
              align="end"
              sideOffset={8}
            >
              <div className="px-3 py-2 text-xs text-foreground-muted font-body">
                {user?.email || "user@example.com"}
              </div>
              <DropdownMenu.Separator className="my-1 divider-gold" />
              <DropdownMenu.Item
                className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm font-body text-status-danger hover:bg-[rgba(230,57,70,0.08)] outline-none transition-colors"
                onSelect={handleLogout}
              >
                <LogOut className="h-4 w-4" />
                Logout
              </DropdownMenu.Item>
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>
    </header>
  );
}

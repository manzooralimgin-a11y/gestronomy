"use client";

import { usePathname, useRouter } from "next/navigation";
import { Bell, LogOut, Menu, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useDashboardStore } from "@/stores/dashboard-store";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CommandBar } from "@/components/layout/command-bar";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

function getBreadcrumbs(pathname: string) {
  const segments = pathname
    .split("/")
    .filter(Boolean);

  if (segments.length === 0) {
    return [{ label: "Dashboard", href: "/" }];
  }

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
    <header className="flex h-14 md:h-16 items-center justify-between border-b border-border bg-card px-3 md:px-6">
      <div className="flex items-center gap-2">
        {/* Hamburger menu — mobile only */}
        <button
          type="button"
          aria-label="Open navigation menu"
          onClick={onMenuToggle}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted md:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Breadcrumbs — hidden on small mobile */}
        <nav className="hidden sm:flex items-center gap-1.5 text-sm">
          {breadcrumbs.map((crumb, index) => (
            <span key={crumb.href} className="flex items-center gap-1.5">
              {index > 0 && <span className="text-muted-foreground/50">/</span>}
              <span
                className={cn(
                  index === breadcrumbs.length - 1
                    ? "font-medium text-foreground"
                    : "text-muted-foreground"
                )}
              >
                {crumb.label}
              </span>
            </span>
          ))}
        </nav>

        {/* Mobile title */}
        <span className="text-sm font-semibold text-foreground sm:hidden">
          {breadcrumbs[breadcrumbs.length - 1]?.label || "Dashboard"}
        </span>
      </div>

      <div className="flex items-center gap-2 md:gap-4">
        <div className="hidden md:block">
          <CommandBar />
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="relative h-9 w-9"
          aria-label="Open alerts"
          onClick={() => router.push("/alerts")}
        >
          <Bell className="h-5 w-5 text-muted-foreground" />
          {unreadCount > 0 && (
            <Badge className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center p-0 text-[10px]">
              {unreadCount > 99 ? "99+" : unreadCount}
            </Badge>
          )}
        </Button>

        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <Button
              variant="ghost"
              className="flex items-center gap-2 px-2"
              aria-label="Open user menu"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-500 text-sm font-medium text-white">
                {user?.full_name
                  ?.split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase() || <User className="h-4 w-4" />}
              </div>
              <span className="hidden text-sm font-medium text-foreground md:block">
                {user?.full_name || "User"}
              </span>
            </Button>
          </DropdownMenu.Trigger>

          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 min-w-[180px] rounded-md border border-border bg-card p-1 shadow-raised"
              align="end"
              sideOffset={8}
            >
              <div className="px-3 py-2 text-sm text-muted-foreground">
                {user?.email || "user@example.com"}
              </div>
              <DropdownMenu.Separator className="my-1 h-px bg-border" />
              <DropdownMenu.Item
                className="flex cursor-pointer items-center gap-2 rounded-sm px-3 py-2 text-sm text-status-danger focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-1 hover:bg-status-danger-soft"
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

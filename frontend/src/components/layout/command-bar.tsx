"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { quickActions, hasRoleAccess } from "@/lib/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { cn } from "@/lib/utils";

export function CommandBar() {
  const router = useRouter();
  const role = useAuthStore((s) => s.user?.role);
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((prev) => !prev);
      } else if (event.key === "Escape") {
        setOpen(false);
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const availableActions = useMemo(() => {
    const visibleActions = quickActions.filter((action) => hasRoleAccess(role, action.minRole));
    if (!query.trim()) {
      return visibleActions;
    }
    const needle = query.toLowerCase();
    return visibleActions.filter(
      (action) =>
        action.label.toLowerCase().includes(needle) ||
        action.description.toLowerCase().includes(needle)
    );
  }, [query, role]);

  const navigateTo = (href: string) => {
    router.push(href);
    setOpen(false);
    setQuery("");
  };

  return (
    <>
      <button
        type="button"
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls="command-bar-dialog"
        onClick={() => setOpen(true)}
        className="group flex h-9 items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 text-sm text-muted-foreground transition duration-fast ease-standard hover:bg-white/[0.08] hover:text-foreground"
      >
        <Search className="h-4 w-4" />
        <span className="hidden lg:inline">Quick actions, pages, workflows</span>
        <span className="inline lg:hidden">Quick actions</span>
        <kbd className="ml-2 hidden rounded border border-border px-1.5 py-0.5 text-[11px] text-muted-foreground lg:inline">
          ⌘K
        </kbd>
      </button>

      {open && (
        <div className="fixed inset-0 z-[100] flex items-start justify-center bg-black/60 backdrop-blur-sm p-4 pt-[12vh]">
          <div
            id="command-bar-dialog"
            role="dialog"
            aria-modal="true"
            className="w-full max-w-2xl overflow-hidden rounded-xl glass shadow-floating glow-subtle"
          >
            <div className="border-b border-white/[0.06] p-3">
              <input
                autoFocus
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search actions (try: reservation, billing, inventory)"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder-muted-foreground outline-none focus:border-[hsl(var(--ring))]"
              />
            </div>

            <div className="max-h-[50vh] overflow-y-auto p-2">
              {availableActions.length === 0 && (
                <div className="rounded-lg px-3 py-6 text-center text-sm text-muted-foreground">
                  No matches for this query.
                </div>
              )}
              {availableActions.map((action) => (
                <button
                  key={action.label}
                  onClick={() => navigateTo(action.href)}
                  className={cn(
                    "w-full rounded-lg px-3 py-2 text-left transition",
                    "hover:bg-muted"
                  )}
                >
                  <p className="text-sm font-medium text-foreground">{action.label}</p>
                  <p className="text-xs text-muted-foreground">{action.description}</p>
                </button>
              ))}
            </div>

            <div className="border-t border-white/[0.06] px-3 py-2 text-xs text-muted-foreground">
              Press <kbd className="rounded border px-1">Esc</kbd> to close
            </div>
          </div>
          <button
            className="absolute inset-0 -z-10"
            aria-label="Close command bar"
            onClick={() => setOpen(false)}
          />
        </div>
      )}
    </>
  );
}

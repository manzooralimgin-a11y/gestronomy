import { create } from "zustand";

interface UIState {
  sidebarCollapsed: boolean;
  sidebarMobileOpen: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (v: boolean) => void;
  setSidebarMobileOpen: (v: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: typeof window !== "undefined"
    ? localStorage.getItem("sidebar-collapsed") === "true"
    : false,
  sidebarMobileOpen: false,

  toggleSidebar: () =>
    set((state) => {
      const next = !state.sidebarCollapsed;
      if (typeof window !== "undefined") {
        localStorage.setItem("sidebar-collapsed", String(next));
      }
      return { sidebarCollapsed: next };
    }),

  setSidebarCollapsed: (v: boolean) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("sidebar-collapsed", String(v));
    }
    set({ sidebarCollapsed: v });
  },

  setSidebarMobileOpen: (v: boolean) => set({ sidebarMobileOpen: v }),
}));

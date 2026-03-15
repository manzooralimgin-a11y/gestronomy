import { create } from "zustand";
import type { User } from "@/lib/auth";

interface AuthState {
  user: User | null;
  token: string | null;
  activeSection: "gestronomy" | "management";
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setActiveSection: (section: "gestronomy" | "management") => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token:
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null,
  activeSection: (typeof window !== "undefined" ? (localStorage.getItem("active_section") as any) : null) || "gestronomy",
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  setActiveSection: (section) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("active_section", section);
    }
    set({ activeSection: section });
  },
  clear: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("active_section");
    }
    set({ user: null, token: null, activeSection: "gestronomy" });
  },
}));

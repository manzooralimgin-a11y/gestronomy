import { create } from "zustand";
import type { User } from "@/lib/auth";

interface AuthState {
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  clear: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token:
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null,
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  clear: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
    set({ user: null, token: null });
  },
}));

import { create } from "zustand";
import { persist } from "zustand/middleware";

export const useOwnerAuthStore = create(
  persist(
    (set) => ({
      owner: null,
      isAuthenticated: false,
      isLoading: true,
      setOwner: (owner) => set({ owner, isAuthenticated: !!owner }),
      setLoading: (isLoading) => set({ isLoading }),
      logout: () => set({ owner: null, isAuthenticated: false }),
    }),
    {
      name: "owner-auth-storage",
      partialize: (state) => ({
        owner: state.owner,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

import { create } from "zustand";

interface AppState {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  commandOpen: boolean;
  setCommandOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  sidebarCollapsed: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  commandOpen: false,
  setCommandOpen: (open) => set({ commandOpen: open }),
}));

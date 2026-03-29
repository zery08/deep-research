import { create } from "zustand";
import type { Source } from "../types";

interface SourceStore {
  sources: Source[];
  selectedIds: Set<string>;

  setSources: (sources: Source[]) => void;
  updateSource: (source: Source) => void;
  removeSource: (id: string) => void;

  toggleSelected: (id: string) => void;
  selectAll: () => void;
  clearSelection: () => void;
}

export const useSourceStore = create<SourceStore>((set) => ({
  sources: [],
  selectedIds: new Set(),

  setSources: (sources) => set({ sources }),

  updateSource: (source) =>
    set((state) => ({
      sources: state.sources.map((s) => (s.id === source.id ? source : s)),
    })),

  removeSource: (id) =>
    set((state) => {
      const selectedIds = new Set(state.selectedIds);
      selectedIds.delete(id);
      return {
        sources: state.sources.filter((s) => s.id !== id),
        selectedIds,
      };
    }),

  toggleSelected: (id) =>
    set((state) => {
      const selectedIds = new Set(state.selectedIds);
      if (selectedIds.has(id)) {
        selectedIds.delete(id);
      } else {
        selectedIds.add(id);
      }
      return { selectedIds };
    }),

  selectAll: () =>
    set((state) => ({
      selectedIds: new Set(
        state.sources.filter((s) => s.status === "ready").map((s) => s.id)
      ),
    })),

  clearSelection: () => set({ selectedIds: new Set() }),
}));

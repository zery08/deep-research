import { create } from "zustand";
import type { ResearchJob, SlideOutline, PPTJob } from "../types";

interface ResearchStore {
  currentJob: ResearchJob | null;
  currentOutline: SlideOutline | null;
  currentPPT: PPTJob | null;

  setJob: (job: ResearchJob | null) => void;
  setOutline: (outline: SlideOutline | null) => void;
  setPPT: (ppt: PPTJob | null) => void;
  reset: () => void;
}

export const useResearchStore = create<ResearchStore>((set) => ({
  currentJob: null,
  currentOutline: null,
  currentPPT: null,

  setJob: (job) => set({ currentJob: job }),
  setOutline: (outline) => set({ currentOutline: outline }),
  setPPT: (ppt) => set({ currentPPT: ppt }),
  reset: () =>
    set({ currentJob: null, currentOutline: null, currentPPT: null }),
}));

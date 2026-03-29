// ---- Source ----

export type SourceType = "pdf" | "pptx" | "url";
export type SourceStatus = "pending" | "indexing" | "ready" | "error";

export interface Source {
  id: string;
  type: SourceType;
  name: string;
  status: SourceStatus;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
}

// ---- Research ----

export type ResearchStatus = "pending" | "running" | "done" | "error";

export interface ResearchJob {
  id: string;
  topic: string;
  source_ids: string[];
  status: ResearchStatus;
  outline_id: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ResearchRequest {
  topic: string;
  source_ids: string[];
}

// ---- Outline ----

export type SlideType = "title" | "section" | "content" | "closing" | "references";

export interface SlideSource {
  source_id: string;
  source_name: string;
  text: string;
  page: number | null;
}

export interface Slide {
  index: number;
  type: SlideType;
  title: string;
  bullets: string[];
  notes: string;
  sources: SlideSource[];
}

export interface SlideOutline {
  id: string;
  research_job_id: string;
  title: string;
  slides: Slide[];
  created_at: string;
  updated_at: string;
}

export interface OutlineUpdateRequest {
  title?: string;
  slides?: Slide[];
}

// ---- PPT ----

export type PPTStatus = "pending" | "generating" | "done" | "error";

export interface PPTJob {
  id: string;
  outline_id: string;
  status: PPTStatus;
  error_message: string | null;
  created_at: string;
}

import axios from "axios";
import type {
  Source,
  ResearchJob,
  ResearchRequest,
  SlideOutline,
  OutlineUpdateRequest,
  PPTJob,
} from "../types";

const api = axios.create({
  baseURL: "/api",
  timeout: 30_000,
});

// ---- Sources ----

export const sourcesApi = {
  list: () => api.get<Source[]>("/sources").then((r) => r.data),

  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api
      .post<Source>("/sources/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  addUrl: (url: string, name?: string) =>
    api.post<Source>("/sources/url", { url, name }).then((r) => r.data),

  get: (id: string) => api.get<Source>(`/sources/${id}`).then((r) => r.data),

  delete: (id: string) => api.delete(`/sources/${id}`),
};

// ---- Research ----

export const researchApi = {
  list: () => api.get<ResearchJob[]>("/research").then((r) => r.data),

  create: (req: ResearchRequest) =>
    api.post<ResearchJob>("/research", req).then((r) => r.data),

  get: (id: string) =>
    api.get<ResearchJob>(`/research/${id}`).then((r) => r.data),
};

// ---- Outline ----

export const outlineApi = {
  create: (research_job_id: string) =>
    api.post<SlideOutline>("/outline", { research_job_id }).then((r) => r.data),

  get: (id: string) =>
    api.get<SlideOutline>(`/outline/${id}`).then((r) => r.data),

  update: (id: string, req: OutlineUpdateRequest) =>
    api.put<SlideOutline>(`/outline/${id}`, req).then((r) => r.data),
};

// ---- PPT ----

export const pptApi = {
  generate: (outline_id: string) =>
    api.post<PPTJob>("/ppt/generate", { outline_id }).then((r) => r.data),

  get: (id: string) => api.get<PPTJob>(`/ppt/${id}`).then((r) => r.data),

  downloadUrl: (id: string) => `/api/ppt/${id}/download`,
};

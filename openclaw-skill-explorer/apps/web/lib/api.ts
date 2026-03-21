import { appConfig } from "./config";

export type RiskFlags = {
  file_read: boolean;
  file_write: boolean;
  network_access: boolean;
  shell_exec: boolean;
  secrets_access: boolean;
  external_download: boolean;
  app_access: boolean;
  unclear_docs: boolean;
};

export type RiskReport = {
  id: number;
  skill_id: number | null;
  input_type: string;
  scanned_at: string;
  risk_level: string;
  risk_score: number;
  flags: RiskFlags;
  matched_keywords: Record<string, string[]>;
  reasons: string[];
  recommendations: string[];
};

export type SkillListItem = {
  name: string;
  slug: string;
  description: string | null;
  category: string | null;
  stars: number;
  last_repo_updated_at: string | null;
  risk_level?: string | null;
};

export type SkillsListResponse = {
  items: SkillListItem[];
  total: number;
  page: number;
  page_size: number;
};

export type SkillDetailResponse = {
  name: string;
  slug: string;
  repo_url: string | null;
  repo_owner: string | null;
  repo_name: string | null;
  description: string | null;
  category: string | null;
  stars: number;
  last_repo_updated_at: string | null;
  latest_risk_report: RiskReport | null;
};

export type SkillQueryParams = {
  q?: string;
  category?: string;
  sort?: "stars_desc" | "updated_desc" | "name_asc";
  page?: number;
  page_size?: number;
};

function buildUrl(path: string, params?: Record<string, string | number | undefined>) {
  const url = new URL(path, appConfig.apiBaseUrl);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value === undefined || value === null || value === "") {
        return;
      }
      url.searchParams.set(key, String(value));
    });
  }
  return url.toString();
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getSkills(params: SkillQueryParams = {}): Promise<SkillsListResponse> {
  const url = buildUrl("/api/skills", params);
  return request<SkillsListResponse>(url);
}

export async function getSkill(slug: string): Promise<SkillDetailResponse> {
  const url = buildUrl(`/api/skills/${slug}`);
  return request<SkillDetailResponse>(url);
}

export async function scanSkill(slug: string): Promise<RiskReport> {
  const url = buildUrl(`/api/skills/${slug}/scan`);
  return request<RiskReport>(url, { method: "POST" });
}

export async function scanText(text: string, type: "readme" | "manifest"): Promise<RiskReport> {
  const url = buildUrl(`/api/scan/${type}`);
  return request<RiskReport>(url, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}


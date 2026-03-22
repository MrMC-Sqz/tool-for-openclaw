"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import SkillCard from "../../../components/SkillCard";
import {
  createSourceSyncJob,
  getScanJob,
  getSource,
  type ScanJobResponse,
  type SourceDetailResponse,
} from "../../../lib/api";

function formatDate(value: string | null): string {
  if (!value) {
    return "Not available";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Not available";
  }
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function syncBadgeStyle(status: string): string {
  const normalized = status.trim().toLowerCase();
  if (normalized === "success" || normalized === "succeeded") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }
  if (normalized === "running" || normalized === "pending") {
    return "border-sky-200 bg-sky-50 text-sky-800";
  }
  if (normalized === "partial") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }
  if (normalized === "failed") {
    return "border-rose-200 bg-rose-50 text-rose-800";
  }
  return "border-slate-200 bg-slate-100 text-slate-700";
}

function sourceTypeLabel(type: string): string {
  const normalized = type.trim().toLowerCase();
  if (normalized === "github_search") {
    return "GitHub Search";
  }
  if (normalized === "generated_catalog") {
    return "Generated Catalog";
  }
  if (normalized === "curated_list") {
    return "Curated Seed";
  }
  if (normalized === "remote_json") {
    return "Remote JSON";
  }
  return type;
}

function SourceDetailSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="h-8 w-1/3 rounded bg-slate-200" />
      <div className="mt-4 h-4 w-2/3 rounded bg-slate-100" />
      <div className="mt-6 grid gap-3 md:grid-cols-3">
        <div className="h-24 rounded-xl bg-slate-100" />
        <div className="h-24 rounded-xl bg-slate-100" />
        <div className="h-24 rounded-xl bg-slate-100" />
      </div>
    </div>
  );
}

export default function SourceDetailPage() {
  const params = useParams<{ id: string }>();
  const sourceId = Number(params?.id ?? "0");

  const [source, setSource] = useState<SourceDetailResponse | null>(null);
  const [job, setJob] = useState<ScanJobResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmittingSync, setIsSubmittingSync] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [skillSearch, setSkillSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");

  useEffect(() => {
    if (!sourceId) {
      setError("Invalid source id.");
      setIsLoading(false);
      return;
    }
    let active = true;

    async function loadSource() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await getSource(sourceId);
        if (!active) {
          return;
        }
        setSource(response);
      } catch (_error) {
        if (!active) {
          return;
        }
        setError("Unable to load source details right now.");
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    loadSource();
    return () => {
      active = false;
    };
  }, [sourceId, reloadKey]);

  useEffect(() => {
    if (!job || !["pending", "running"].includes(job.status)) {
      return;
    }
    const handle = window.setInterval(async () => {
      try {
        const refreshed = await getScanJob(job.id);
        setJob(refreshed);
        if (["succeeded", "failed"].includes(refreshed.status)) {
          window.clearInterval(handle);
          setReloadKey((previous) => previous + 1);
        }
      } catch {
        window.clearInterval(handle);
      }
    }, 2000);
    return () => window.clearInterval(handle);
  }, [job]);

  const handleStartSync = async () => {
    if (!sourceId) {
      return;
    }
    setIsSubmittingSync(true);
    setError(null);
    try {
      const created = await createSourceSyncJob(sourceId);
      const initialJob = await getScanJob(created.job_id);
      setJob(initialJob);
    } catch (_error) {
      setError("Unable to start source sync right now.");
    } finally {
      setIsSubmittingSync(false);
    }
  };

  const filteredSkills = useMemo(() => {
    if (!source) {
      return [];
    }
    const normalizedSearch = skillSearch.trim().toLowerCase();
    return source.skills.filter((skill) => {
      const matchesSearch =
        !normalizedSearch ||
        skill.name.toLowerCase().includes(normalizedSearch) ||
        (skill.description || "").toLowerCase().includes(normalizedSearch);
      const matchesRisk = !riskFilter || (skill.risk_level || "unknown") === riskFilter;
      const matchesCategory = !categoryFilter || (skill.category || "uncategorized") === categoryFilter;
      return matchesSearch && matchesRisk && matchesCategory;
    });
  }, [source, skillSearch, riskFilter, categoryFilter]);

  const categoryOptions = useMemo(() => {
    if (!source) {
      return [];
    }
    return Array.from(new Set(source.skills.map((skill) => skill.category || "uncategorized"))).sort();
  }, [source]);

  const riskOptions = useMemo(() => {
    if (!source) {
      return [];
    }
    return Array.from(new Set(source.skills.map((skill) => skill.risk_level || "unknown"))).sort();
  }, [source]);

  if (isLoading) {
    return (
      <main className="mx-auto w-full max-w-6xl px-6 py-8">
        <SourceDetailSkeleton />
      </main>
    );
  }

  if (!source) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-8">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <p className="text-slate-700">{error || "Source not found."}</p>
          <button
            type="button"
            onClick={() => setReloadKey((previous) => previous + 1)}
            className="mt-3 rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            aria-label="Retry loading source"
          >
            Retry
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-8">
      <Link href="/sources" className="text-sm text-slate-600 hover:text-slate-900">
        {"<- Back to sources"}
      </Link>

      {error ? (
        <div className="mt-4 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
          <p>{error}</p>
        </div>
      ) : null}

      <section className="mt-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              Source Detail
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{source.name}</h1>
            <p className="mt-2 text-sm text-slate-600">{sourceTypeLabel(source.type)}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className={`rounded-md border px-2 py-1 text-xs font-medium ${syncBadgeStyle(source.sync_status)}`}>
                {source.sync_status}
              </span>
              <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700">
                {source.is_active === 1 ? "Active" : "Paused"}
              </span>
            </div>
          </div>
          <div className="flex flex-col items-start gap-3">
            <button
              type="button"
              onClick={handleStartSync}
              disabled={isSubmittingSync || ["pending", "running"].includes(job?.status || "")}
              className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              aria-label="Start source sync"
            >
              {isSubmittingSync || ["pending", "running"].includes(job?.status || "") ? "Syncing..." : "Sync This Source"}
            </button>
            <button
              type="button"
              onClick={() => setReloadKey((previous) => previous + 1)}
              className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              aria-label="Refresh source detail"
            >
              Refresh Detail
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Skills</p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">{source.skill_count}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Last Synced</p>
            <p className="mt-2 text-sm font-medium text-slate-900">{formatDate(source.last_synced_at)}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Updated</p>
            <p className="mt-2 text-sm font-medium text-slate-900">{formatDate(source.updated_at)}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Endpoint</p>
            {source.base_url ? (
              <a
                href={source.base_url}
                target="_blank"
                rel="noreferrer"
                className="mt-2 block break-all text-sm text-sky-700 hover:text-sky-800"
              >
                {source.base_url}
              </a>
            ) : (
              <p className="mt-2 text-sm text-slate-600">Local or generated source.</p>
            )}
          </div>
        </div>
      </section>

      {job ? (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Latest sync job</h2>
              <p className="mt-1 text-sm text-slate-600">
                Track the current source refresh without leaving the page.
              </p>
            </div>
            <span className={`rounded-md border px-2 py-1 text-xs font-medium ${syncBadgeStyle(job.status)}`}>
              {job.status}
            </span>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
              <p className="font-medium text-slate-900">Created</p>
              <p className="mt-1">{formatDate(job.created_at)}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
              <p className="font-medium text-slate-900">Started</p>
              <p className="mt-1">{formatDate(job.started_at)}</p>
            </div>
            <div className="rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
              <p className="font-medium text-slate-900">Finished</p>
              <p className="mt-1">{formatDate(job.finished_at)}</p>
            </div>
          </div>
          {job.result?.stats ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
              {JSON.stringify(job.result.stats, null, 2)}
            </pre>
          ) : null}
          {job.error_message ? (
            <p className="mt-4 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
              {job.error_message}
            </p>
          ) : null}
        </section>
      ) : null}

      <section className="mt-6 grid gap-4 md:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Category breakdown</h2>
          <div className="mt-4 space-y-3">
            {Object.entries(source.categories).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700">
                <span>{category}</span>
                <span className="font-semibold text-slate-900">{count}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Risk breakdown</h2>
          <div className="mt-4 space-y-3">
            {Object.entries(source.risk_levels).map(([riskLevel, count]) => (
              <div key={riskLevel} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700">
                <span>{riskLevel}</span>
                <span className="font-semibold text-slate-900">{count}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900">Indexed skills</h2>
        <p className="mt-1 text-sm text-slate-600">
          Filter the skills currently coming from this source.
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto_auto]">
          <input
            value={skillSearch}
            onChange={(event) => setSkillSearch(event.target.value)}
            placeholder="Search skills within this source"
            aria-label="Search source skills"
            className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none ring-slate-300 focus:ring-2"
          />
          <select
            value={categoryFilter}
            onChange={(event) => setCategoryFilter(event.target.value)}
            aria-label="Filter source skills by category"
            className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
          >
            <option value="">All categories</option>
            {categoryOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <select
            value={riskFilter}
            onChange={(event) => setRiskFilter(event.target.value)}
            aria-label="Filter source skills by risk"
            className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
          >
            <option value="">All risks</option>
            {riskOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </section>

      {filteredSkills.length > 0 ? (
        <section className="mt-6 grid gap-4">
          {filteredSkills.map((skill) => (
            <SkillCard
              key={skill.slug}
              name={skill.name}
              slug={skill.slug}
              description={skill.description}
              category={skill.category}
              stars={skill.stars}
              updated_at={skill.last_repo_updated_at}
              risk_level={skill.risk_level ?? null}
            />
          ))}
        </section>
      ) : (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">No skills match</h2>
          <p className="mt-2 text-sm text-slate-600">
            Try another source-scope search term or reset the category and risk filters.
          </p>
          <button
            type="button"
            onClick={() => {
              setSkillSearch("");
              setRiskFilter("");
              setCategoryFilter("");
            }}
            className="mt-4 rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            aria-label="Reset source skill filters"
          >
            Reset Filters
          </button>
        </section>
      )}
    </main>
  );
}

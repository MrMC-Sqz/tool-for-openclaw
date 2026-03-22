"use client";

import { useEffect, useMemo, useState } from "react";

import { getSources, type SourceListItem } from "../../lib/api";

function formatDate(value: string | null): string {
  if (!value) {
    return "Not synced yet";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Not synced yet";
  }
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function syncBadgeStyle(status: string): string {
  const normalized = status.trim().toLowerCase();
  if (normalized === "success") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }
  if (normalized === "running") {
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
  if (normalized === "curated_seed") {
    return "Curated Seed";
  }
  if (normalized === "remote_json") {
    return "Remote JSON";
  }
  return type;
}

function SourceCardSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="h-5 w-1/3 rounded bg-slate-200" />
      <div className="mt-3 h-4 w-1/2 rounded bg-slate-100" />
      <div className="mt-4 h-4 w-full rounded bg-slate-100" />
      <div className="mt-2 h-4 w-4/5 rounded bg-slate-100" />
    </div>
  );
}

export default function SourcesPage() {
  const [items, setItems] = useState<SourceListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function loadSources() {
      setIsLoading(true);
      setError(null);
      try {
        const response = await getSources();
        if (!active) {
          return;
        }
        setItems(response.items);
      } catch (_error) {
        if (!active) {
          return;
        }
        setError("Unable to load source coverage right now. Retry after the API is available.");
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    loadSources();
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const summary = useMemo(() => {
    const totalSkills = items.reduce((accumulator, source) => accumulator + source.skill_count, 0);
    const healthySources = items.filter((source) => source.sync_status === "success").length;
    const publicSources = items.filter((source) =>
      ["github_search", "generated_catalog", "remote_json"].includes(source.type),
    ).length;
    const activeSources = items.filter((source) => source.is_active === 1).length;
    return {
      totalSkills,
      healthySources,
      publicSources,
      activeSources,
    };
  }, [items]);

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-8">
      <section className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">
              Source Coverage
            </p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
              Public and curated sources
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              Monitor which catalogs feed the skill index, how recently they synced, and how much
              searchable coverage each one contributes.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setReloadKey((previous) => previous + 1)}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            aria-label="Refresh source coverage"
          >
            Refresh Sources
          </button>
        </div>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-4">
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Total Sources
          </p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{items.length}</p>
          <p className="mt-2 text-sm text-slate-600">{summary.activeSources} active for sync</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Indexed Skills
          </p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{summary.totalSkills}</p>
          <p className="mt-2 text-sm text-slate-600">Coverage across curated and public inputs</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Healthy Syncs
          </p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{summary.healthySources}</p>
          <p className="mt-2 text-sm text-slate-600">Sources currently reporting success</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Public Reach
          </p>
          <p className="mt-3 text-3xl font-semibold text-slate-900">{summary.publicSources}</p>
          <p className="mt-2 text-sm text-slate-600">GitHub and generated public catalogs</p>
        </article>
      </section>

      {error ? (
        <section className="mt-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          <p>{error}</p>
          <button
            type="button"
            onClick={() => setReloadKey((previous) => previous + 1)}
            className="mt-3 rounded-md border border-rose-300 px-3 py-1.5 font-medium text-rose-700 hover:bg-rose-100"
            aria-label="Retry loading sources"
          >
            Retry
          </button>
        </section>
      ) : null}

      {isLoading ? (
        <section className="mt-6 grid gap-4 md:grid-cols-2">
          <SourceCardSkeleton />
          <SourceCardSkeleton />
          <SourceCardSkeleton />
          <SourceCardSkeleton />
        </section>
      ) : null}

      {!isLoading && items.length === 0 ? (
        <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">No sources available</h2>
          <p className="mt-2 text-sm text-slate-600">
            Sync the catalog to register curated or public sources in the index.
          </p>
        </section>
      ) : null}

      {!isLoading && items.length > 0 ? (
        <section className="mt-6 grid gap-4 md:grid-cols-2">
          {items.map((source) => (
            <article
              key={source.id}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow-md"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">{source.name}</h2>
                  <p className="mt-1 text-sm text-slate-600">{sourceTypeLabel(source.type)}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span
                    className={`rounded-md border px-2 py-1 text-xs font-medium ${syncBadgeStyle(source.sync_status)}`}
                  >
                    {source.sync_status}
                  </span>
                  <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700">
                    {source.is_active === 1 ? "Active" : "Paused"}
                  </span>
                </div>
              </div>

              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <div className="rounded-xl bg-slate-50 p-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Skill Count
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-slate-900">{source.skill_count}</p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Last Synced
                  </p>
                  <p className="mt-2 text-sm font-medium text-slate-900">
                    {formatDate(source.last_synced_at)}
                  </p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Updated
                  </p>
                  <p className="mt-2 text-sm font-medium text-slate-900">
                    {formatDate(source.updated_at)}
                  </p>
                </div>
              </div>

              <div className="mt-4 border-t border-slate-100 pt-4">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Source Endpoint
                </p>
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
                  <p className="mt-2 text-sm text-slate-600">
                    Managed locally through seed data or generated catalog rules.
                  </p>
                )}
              </div>
            </article>
          ))}
        </section>
      ) : null}
    </main>
  );
}

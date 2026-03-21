"use client";

import { useEffect, useMemo, useState } from "react";

import SearchBar from "../../components/SearchBar";
import SkillCard from "../../components/SkillCard";
import { getSkills, type SkillListItem, type SkillsListResponse } from "../../lib/api";
import { demoSkills } from "../../lib/demoData";

const PAGE_SIZE = 10;

function SkillCardSkeleton() {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="h-5 w-2/5 rounded bg-slate-200" />
      <div className="mt-3 h-4 w-full rounded bg-slate-100" />
      <div className="mt-2 h-4 w-4/5 rounded bg-slate-100" />
      <div className="mt-4 h-3 w-3/5 rounded bg-slate-100" />
    </div>
  );
}

export default function SkillsPage() {
  const [skillsResponse, setSkillsResponse] = useState<SkillsListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUsingDemoData, setIsUsingDemoData] = useState(false);

  const [queryInput, setQueryInput] = useState("");
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [sort, setSort] = useState<"stars_desc" | "updated_desc" | "name_asc">("stars_desc");
  const [page, setPage] = useState(1);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    async function loadSkills() {
      setIsLoading(true);
      setError(null);
      setIsUsingDemoData(false);
      try {
        const hasActiveFilters = Boolean(query || category);
        const data = await getSkills({
          q: query || undefined,
          category: category || undefined,
          sort,
          page,
          page_size: PAGE_SIZE,
        });

        if (!active) {
          return;
        }

        if (data.items.length === 0 && !hasActiveFilters) {
          setSkillsResponse({
            items: demoSkills,
            total: demoSkills.length,
            page: 1,
            page_size: PAGE_SIZE,
          });
          setIsUsingDemoData(true);
        } else {
          setSkillsResponse(data);
        }
      } catch (_loadError) {
        if (!active) {
          return;
        }
        setError("Unable to load live skills right now. Showing demo data.");
        setSkillsResponse({
          items: demoSkills,
          total: demoSkills.length,
          page: 1,
          page_size: PAGE_SIZE,
        });
        setIsUsingDemoData(true);
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    loadSkills();
    return () => {
      active = false;
    };
  }, [query, category, sort, page, reloadKey]);

  const items = skillsResponse?.items ?? [];
  const total = skillsResponse?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const categoryOptions = useMemo(() => {
    const set = new Set<string>();
    [...items, ...demoSkills].forEach((item: SkillListItem) => {
      if (item.category) {
        set.add(item.category);
      }
    });
    return Array.from(set).sort();
  }, [items]);

  const hasSearchFilters = Boolean(query || category);

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-8">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Skills</h1>
      <p className="mt-2 text-sm text-slate-600">
        Explore skills, compare risk posture, and open details for recommendations.
      </p>

      <section className="mt-6 grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-[1fr_auto_auto_auto]">
        <SearchBar
          value={queryInput}
          onChange={setQueryInput}
          placeholder="Search by name, summary, category, or tags"
        />
        <select
          value={category}
          onChange={(event) => {
            setCategory(event.target.value);
            setPage(1);
          }}
          aria-label="Filter by category"
          className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
        >
          <option value="">All categories</option>
          {categoryOptions.map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
        <select
          value={sort}
          onChange={(event) => {
            setSort(event.target.value as "stars_desc" | "updated_desc" | "name_asc");
            setPage(1);
          }}
          aria-label="Sort skills"
          className="rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
        >
          <option value="stars_desc">Sort: Stars</option>
          <option value="updated_desc">Sort: Updated</option>
          <option value="name_asc">Sort: Name</option>
        </select>
        <button
          type="button"
          onClick={() => {
            setQuery(queryInput.trim());
            setPage(1);
          }}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          aria-label="Search skills"
        >
          Search
        </button>
      </section>

      {isUsingDemoData ? (
        <p className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Demo mode: showing fallback sample skills.
        </p>
      ) : null}

      {error ? (
        <div className="mt-4 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
          <p>{error}</p>
          <button
            type="button"
            onClick={() => setReloadKey((prev) => prev + 1)}
            className="mt-2 rounded-md border border-rose-300 px-3 py-1 font-medium text-rose-700 hover:bg-rose-100"
            aria-label="Retry loading skills"
          >
            Retry
          </button>
        </div>
      ) : null}

      {isLoading ? (
        <section className="mt-6 grid gap-4">
          <SkillCardSkeleton />
          <SkillCardSkeleton />
          <SkillCardSkeleton />
        </section>
      ) : null}

      {!isLoading && items.length === 0 ? (
        <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">No skills found</h2>
          <p className="mt-2 text-sm text-slate-600">
            {hasSearchFilters
              ? "Try a different keyword or clear filters."
              : "No skills are available yet. Try syncing seed data."}
          </p>
          <button
            type="button"
            onClick={() => {
              setQueryInput("");
              setQuery("");
              setCategory("");
              setSort("stars_desc");
              setPage(1);
              setReloadKey((prev) => prev + 1);
            }}
            className="mt-4 rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            aria-label="Reset filters"
          >
            Reset Filters
          </button>
        </section>
      ) : null}

      {!isLoading && items.length > 0 ? (
        <section className="mt-6 grid gap-4">
          {items.map((skill) => (
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
      ) : null}

      {!isLoading && items.length > 0 ? (
        <div className="mt-6 flex items-center justify-between text-sm">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((prev) => Math.max(1, prev - 1))}
            className="rounded-md border border-slate-300 px-3 py-2 text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Previous page"
          >
            Previous
          </button>
          <span className="text-slate-600">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
            className="rounded-md border border-slate-300 px-3 py-2 text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
            aria-label="Next page"
          >
            Next
          </button>
        </div>
      ) : null}
    </main>
  );
}

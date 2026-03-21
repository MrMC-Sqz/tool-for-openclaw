"use client";

import { useEffect, useMemo, useState } from "react";

import SearchBar from "../../components/SearchBar";
import SkillCard from "../../components/SkillCard";
import { getSkills, type SkillListItem, type SkillsListResponse } from "../../lib/api";

const PAGE_SIZE = 10;

export default function SkillsPage() {
  const [skillsResponse, setSkillsResponse] = useState<SkillsListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [queryInput, setQueryInput] = useState("");
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [sort, setSort] = useState<"stars_desc" | "updated_desc" | "name_asc">("stars_desc");
  const [page, setPage] = useState(1);

  useEffect(() => {
    let active = true;
    async function loadSkills() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getSkills({
          q: query || undefined,
          category: category || undefined,
          sort,
          page,
          page_size: PAGE_SIZE,
        });
        if (active) {
          setSkillsResponse(data);
        }
      } catch (loadError) {
        if (active) {
          setError("Failed to load skills.");
        }
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
  }, [query, category, sort, page]);

  const items = skillsResponse?.items ?? [];
  const total = skillsResponse?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const categoryOptions = useMemo(() => {
    const set = new Set<string>();
    items.forEach((item: SkillListItem) => {
      if (item.category) {
        set.add(item.category);
      }
    });
    return Array.from(set).sort();
  }, [items]);

  return (
    <main className="mx-auto w-full max-w-6xl px-6 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Skills</h1>
      <p className="mt-1 text-sm text-slate-600">Browse skills and inspect their metadata.</p>

      <section className="mt-6 grid gap-3 rounded-lg border border-slate-200 bg-white p-4 md:grid-cols-[1fr_auto_auto_auto]">
        <SearchBar value={queryInput} onChange={setQueryInput} />
        <select
          value={category}
          onChange={(event) => {
            setCategory(event.target.value);
            setPage(1);
          }}
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
        >
          Search
        </button>
      </section>

      {isLoading ? <p className="mt-6 text-sm text-slate-600">Loading skills...</p> : null}
      {error ? <p className="mt-6 text-sm text-rose-600">{error}</p> : null}

      {!isLoading && !error && items.length === 0 ? (
        <p className="mt-6 text-sm text-slate-600">No data.</p>
      ) : null}

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

      <div className="mt-6 flex items-center justify-between text-sm">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => setPage((prev) => Math.max(1, prev - 1))}
          className="rounded-md border border-slate-300 px-3 py-2 text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
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
        >
          Next
        </button>
      </div>
    </main>
  );
}


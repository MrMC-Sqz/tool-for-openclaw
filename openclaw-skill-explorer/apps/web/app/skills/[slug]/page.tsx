"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import RiskCard from "../../../components/RiskCard";
import SkillCard from "../../../components/SkillCard";
import {
  getSimilarSkills,
  getSkill,
  scanSkill,
  type SkillDetailResponse,
  type SkillListItem,
} from "../../../lib/api";
import { demoSkillDetails, demoSkills } from "../../../lib/demoData";

function formatDate(value: string | null): string {
  if (!value) {
    return "Unknown";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }
  return date.toLocaleString();
}

function DetailSkeleton() {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="h-8 w-1/2 rounded bg-slate-200" />
      <div className="mt-4 h-4 w-full rounded bg-slate-100" />
      <div className="mt-2 h-4 w-4/5 rounded bg-slate-100" />
      <div className="mt-6 h-10 w-32 rounded bg-slate-200" />
    </div>
  );
}

export default function SkillDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = params?.slug ?? "";

  const [skill, setSkill] = useState<SkillDetailResponse | null>(null);
  const [similarSkills, setSimilarSkills] = useState<SkillListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUsingDemoData, setIsUsingDemoData] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  const fallbackSkill = useMemo(() => {
    if (!slug) {
      return demoSkillDetails["openclaw-workflow-runner"];
    }
    return demoSkillDetails[slug] ?? demoSkillDetails["openclaw-workflow-runner"];
  }, [slug]);

  const loadSkill = async () => {
    if (!slug) {
      return;
    }
    setIsLoading(true);
    setError(null);
    setIsUsingDemoData(false);
    try {
      const [detail, similar] = await Promise.all([getSkill(slug), getSimilarSkills(slug, 5)]);
      setSkill(detail);
      if (similar.items.length === 0) {
        setSimilarSkills(demoSkills.filter((item) => item.slug !== detail.slug).slice(0, 3));
      } else {
        setSimilarSkills(similar.items);
      }
    } catch (_loadError) {
      setError("Unable to load live skill details. Showing demo content.");
      setSkill(fallbackSkill);
      setSimilarSkills(demoSkills.filter((item) => item.slug !== fallbackSkill.slug).slice(0, 3));
      setIsUsingDemoData(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSkill();
  }, [slug, reloadKey]);

  const handleScan = async () => {
    if (!slug || isUsingDemoData) {
      return;
    }
    setIsScanning(true);
    setError(null);
    try {
      await scanSkill(slug);
      await loadSkill();
    } catch (_scanError) {
      setError("Failed to run risk scan. Please try again.");
    } finally {
      setIsScanning(false);
    }
  };

  if (isLoading) {
    return (
      <main className="mx-auto w-full max-w-5xl px-6 py-8">
        <DetailSkeleton />
      </main>
    );
  }

  if (!skill) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-8">
        <section className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <p className="text-slate-700">Skill not available.</p>
          <button
            type="button"
            onClick={() => setReloadKey((prev) => prev + 1)}
            className="mt-3 rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            aria-label="Retry loading skill"
          >
            Retry
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-8">
      <Link href="/skills" className="text-sm text-slate-600 hover:text-slate-900">
        {"<- Back to skills"}
      </Link>

      {isUsingDemoData ? (
        <p className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Demo mode: showing fallback detail data.
        </p>
      ) : null}

      {error ? (
        <div className="mt-4 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
          <p>{error}</p>
          <button
            type="button"
            onClick={() => setReloadKey((prev) => prev + 1)}
            className="mt-2 rounded-md border border-rose-300 px-3 py-1 font-medium text-rose-700 hover:bg-rose-100"
            aria-label="Retry loading skill details"
          >
            Retry
          </button>
        </div>
      ) : null}

      <section className="mt-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Overview</h2>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{skill.name}</h1>
        <p className="mt-3 text-sm leading-6 text-slate-700">
          {skill.description || "No description provided."}
        </p>
        {skill.readme_summary ? (
          <p className="mt-4 rounded-md bg-slate-50 p-3 text-sm leading-6 text-slate-600">
            {skill.readme_summary}
          </p>
        ) : null}
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-600">
          <span>Category: {skill.category || "Uncategorized"}</span>
          <span>Stars: {skill.stars}</span>
          <span>Last updated: {formatDate(skill.last_repo_updated_at)}</span>
        </div>
        <button
          type="button"
          onClick={handleScan}
          disabled={isScanning || isUsingDemoData}
          className="mt-5 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          aria-label="Run risk scan"
        >
          {isScanning ? "Scanning..." : isUsingDemoData ? "Scan unavailable in demo mode" : "Run Risk Scan"}
        </button>
      </section>

      <section className="mt-6">
        <h2 className="mb-3 text-xl font-semibold text-slate-900">Risk Analysis</h2>
        {skill.latest_risk_report ? (
          <RiskCard
            risk_level={skill.latest_risk_report.risk_level}
            risk_score={skill.latest_risk_report.risk_score}
            flags={skill.latest_risk_report.flags}
            reasons={skill.latest_risk_report.reasons}
            recommendations={skill.latest_risk_report.recommendations}
          />
        ) : (
          <p className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600 shadow-sm">
            No risk report available yet. Run a scan to generate one.
          </p>
        )}
      </section>

      <section className="mt-6">
        <h2 className="mb-3 text-xl font-semibold text-slate-900">Recommendations</h2>
        {skill.latest_risk_report?.recommendations?.length ? (
          <ul className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-700 shadow-sm">
            {skill.latest_risk_report.recommendations.map((item) => (
              <li key={item} className="ml-4 list-disc py-1">
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600 shadow-sm">
            No recommendations available.
          </p>
        )}
      </section>

      <section className="mt-6">
        <h2 className="mb-3 text-xl font-semibold text-slate-900">Similar Skills</h2>
        {similarSkills.length > 0 ? (
          <div className="grid gap-4">
            {similarSkills.map((item) => (
              <SkillCard
                key={item.slug}
                name={item.name}
                slug={item.slug}
                description={item.description}
                category={item.category}
                stars={item.stars}
                updated_at={item.last_repo_updated_at}
                risk_level={item.risk_level ?? null}
              />
            ))}
          </div>
        ) : (
          <p className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600 shadow-sm">
            No similar skills found.
          </p>
        )}
      </section>
    </main>
  );
}

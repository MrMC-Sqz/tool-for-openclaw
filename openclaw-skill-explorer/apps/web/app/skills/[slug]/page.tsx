"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import RiskCard from "../../../components/RiskCard";
import { getSkill, scanSkill, type SkillDetailResponse } from "../../../lib/api";

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

export default function SkillDetailPage() {
  const params = useParams<{ slug: string }>();
  const slug = params?.slug ?? "";

  const [skill, setSkill] = useState<SkillDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSkill = async () => {
    if (!slug) {
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const data = await getSkill(slug);
      setSkill(data);
    } catch (loadError) {
      setError("Failed to load skill.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSkill();
  }, [slug]);

  const handleScan = async () => {
    if (!slug) {
      return;
    }
    setIsScanning(true);
    setError(null);
    try {
      await scanSkill(slug);
      await loadSkill();
    } catch (scanError) {
      setError("Failed to run risk scan.");
    } finally {
      setIsScanning(false);
    }
  };

  if (isLoading) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-8">
        <p className="text-sm text-slate-600">Loading skill...</p>
      </main>
    );
  }

  if (error && !skill) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-8">
        <p className="text-sm text-rose-600">{error}</p>
      </main>
    );
  }

  if (!skill) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-8">
        <p className="text-sm text-slate-600">No data.</p>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-8">
      <Link href="/skills" className="text-sm text-slate-600 hover:text-slate-900">
        {"<- Back to skills"}
      </Link>

      <section className="mt-4 rounded-lg border border-slate-200 bg-white p-5">
        <h1 className="text-2xl font-bold text-slate-900">{skill.name}</h1>
        <p className="mt-2 text-sm text-slate-600">
          {skill.description || "No description provided."}
        </p>
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-600">
          <span>Category: {skill.category || "Uncategorized"}</span>
          <span>Stars: {skill.stars}</span>
          <span>Last updated: {formatDate(skill.last_repo_updated_at)}</span>
        </div>
        <button
          type="button"
          onClick={handleScan}
          disabled={isScanning}
          className="mt-5 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isScanning ? "Scanning..." : "Run Risk Scan"}
        </button>
        {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}
      </section>

      <section className="mt-6">
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Risk Analysis</h2>
        {skill.latest_risk_report ? (
          <RiskCard
            risk_level={skill.latest_risk_report.risk_level}
            risk_score={skill.latest_risk_report.risk_score}
            flags={skill.latest_risk_report.flags}
            reasons={skill.latest_risk_report.reasons}
            recommendations={skill.latest_risk_report.recommendations}
          />
        ) : (
          <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
            No risk report available yet.
          </p>
        )}
      </section>
    </main>
  );
}

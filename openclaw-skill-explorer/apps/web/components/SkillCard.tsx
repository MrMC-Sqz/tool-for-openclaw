import Link from "next/link";

type SkillCardProps = {
  name: string;
  slug: string;
  description: string | null;
  category: string | null;
  stars: number;
  updated_at: string | null;
  risk_level?: string | null;
};

function formatDate(value: string | null): string {
  if (!value) {
    return "Unknown";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }
  return date.toLocaleDateString();
}

function truncate(value: string, max = 140): string {
  if (value.length <= max) {
    return value;
  }
  return `${value.slice(0, max - 1).trimEnd()}...`;
}

function riskBadgeStyle(level: string | null | undefined): string {
  const normalized = (level || "").toUpperCase();
  if (normalized === "LOW") {
    return "border-emerald-200 bg-emerald-50 text-emerald-800";
  }
  if (normalized === "MEDIUM") {
    return "border-amber-200 bg-amber-50 text-amber-800";
  }
  if (normalized === "HIGH") {
    return "border-orange-200 bg-orange-50 text-orange-800";
  }
  if (normalized === "CRITICAL") {
    return "border-rose-200 bg-rose-50 text-rose-800";
  }
  return "border-slate-200 bg-slate-100 text-slate-700";
}

export default function SkillCard({
  name,
  slug,
  description,
  category,
  stars,
  updated_at,
  risk_level,
}: SkillCardProps) {
  return (
    <Link
      href={`/skills/${slug}`}
      className="group block rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
      aria-label={`Open skill ${name}`}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold text-slate-900 transition group-hover:text-slate-700">{name}</h3>
        <span
          className={`rounded-md border px-2 py-1 text-xs font-medium ${riskBadgeStyle(risk_level)}`}
          aria-label={`Risk level ${risk_level ?? "No risk data"}`}
        >
          {risk_level ?? "No risk data"}
        </span>
      </div>
      <p className="mt-2 text-sm text-slate-600">
        {description ? truncate(description) : "No description provided."}
      </p>
      <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
        <span className="font-medium">Category: {category || "Uncategorized"}</span>
        <span className="font-medium">Stars: {stars}</span>
        <span className="font-medium">Updated: {formatDate(updated_at)}</span>
      </div>
    </Link>
  );
}

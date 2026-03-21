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
      className="block rounded-lg border border-slate-200 bg-white p-4 hover:border-slate-300"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-base font-semibold text-slate-900">{name}</h3>
        <span className="rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
          {risk_level ?? "No risk data"}
        </span>
      </div>
      <p className="mt-2 text-sm text-slate-600">
        {description || "No description provided."}
      </p>
      <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-500">
        <span>Category: {category || "Uncategorized"}</span>
        <span>Stars: {stars}</span>
        <span>Updated: {formatDate(updated_at)}</span>
      </div>
    </Link>
  );
}

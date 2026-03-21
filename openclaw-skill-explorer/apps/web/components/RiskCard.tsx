import type { RiskFlags } from "../lib/api";

type RiskCardProps = {
  risk_level: string;
  risk_score: number;
  flags: RiskFlags;
  reasons: string[];
  recommendations: string[];
};

const levelStyle: Record<string, string> = {
  LOW: "bg-emerald-100 text-emerald-800",
  MEDIUM: "bg-amber-100 text-amber-800",
  HIGH: "bg-orange-100 text-orange-800",
  CRITICAL: "bg-rose-100 text-rose-800",
};

function formatFlagName(flag: string) {
  return flag.replaceAll("_", " ");
}

export default function RiskCard({
  risk_level,
  risk_score,
  flags,
  reasons,
  recommendations,
}: RiskCardProps) {
  const activeFlags = Object.entries(flags).filter(([, enabled]) => enabled);
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-center gap-3">
        <span
          className={`rounded px-3 py-1 text-sm font-semibold ${levelStyle[risk_level] || "bg-slate-100 text-slate-700"}`}
        >
          {risk_level}
        </span>
        <span className="text-sm font-medium text-slate-700">Risk score: {risk_score}</span>
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-semibold text-slate-900">Capability Flags</h3>
        {activeFlags.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No risky capabilities detected.</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {activeFlags.map(([flag]) => (
              <span
                key={flag}
                className="rounded bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700"
              >
                {formatFlagName(flag)}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-semibold text-slate-900">Reasons</h3>
        {reasons.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No reasons available.</p>
        ) : (
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
            {reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="mt-4">
        <h3 className="text-sm font-semibold text-slate-900">Recommendations</h3>
        {recommendations.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No recommendations available.</p>
        ) : (
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
            {recommendations.map((recommendation) => (
              <li key={recommendation}>{recommendation}</li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}


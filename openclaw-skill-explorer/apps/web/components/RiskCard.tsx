import type { RiskFlags } from "../lib/api";

type RiskCardProps = {
  risk_level: string;
  risk_score: number;
  flags: RiskFlags;
  reasons: string[];
  recommendations: string[];
};

const levelStyle: Record<string, string> = {
  LOW: "border-emerald-200 bg-emerald-50 text-emerald-800",
  MEDIUM: "border-amber-200 bg-amber-50 text-amber-800",
  HIGH: "border-orange-200 bg-orange-50 text-orange-800",
  CRITICAL: "border-rose-200 bg-rose-50 text-rose-800",
};

function formatFlagName(flag: string) {
  return flag.replaceAll("_", " ");
}

const flagPriority: Record<string, number> = {
  secrets_access: 0,
  shell_exec: 1,
  external_download: 2,
  network_access: 3,
  file_write: 4,
  app_access: 5,
  file_read: 6,
  unclear_docs: 7,
};

export default function RiskCard({
  risk_level,
  risk_score,
  flags,
  reasons,
  recommendations,
}: RiskCardProps) {
  const normalizedLevel = risk_level.toUpperCase();
  const activeFlags = Object.entries(flags)
    .filter(([, enabled]) => enabled)
    .sort((a, b) => {
      const aWeight = flagPriority[a[0]] ?? 99;
      const bWeight = flagPriority[b[0]] ?? 99;
      return aWeight - bWeight;
    });
  const topFactors = activeFlags.slice(0, 3);

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <span
            className={`rounded-md border px-3 py-1 text-sm font-semibold ${levelStyle[normalizedLevel] || "border-slate-200 bg-slate-100 text-slate-700"}`}
          >
            {normalizedLevel}
          </span>
          <span className="text-sm font-medium text-slate-700">Risk level</span>
        </div>
        <div className="text-right">
          <p className="text-xs uppercase tracking-wide text-slate-500">Risk score</p>
          <p className="text-2xl font-bold text-slate-900">{risk_score}</p>
        </div>
      </div>

      <div className="mt-5">
        <h3 className="text-sm font-semibold text-slate-900">Top Risk Factors</h3>
        {topFactors.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No major risk factors detected.</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {topFactors.map(([flag]) => (
              <span
                key={`top-${flag}`}
                className="rounded-full bg-slate-900 px-3 py-1 text-xs font-medium text-white"
              >
                {formatFlagName(flag)}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-5">
        <h3 className="text-sm font-semibold text-slate-900">Capability Flags</h3>
        {activeFlags.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">No risky capabilities detected.</p>
        ) : (
          <div className="mt-2 flex flex-wrap gap-2">
            {activeFlags.map(([flag]) => (
              <span
                key={flag}
                className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium capitalize text-slate-700"
              >
                {formatFlagName(flag)}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="mt-5">
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

      <div className="mt-5">
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

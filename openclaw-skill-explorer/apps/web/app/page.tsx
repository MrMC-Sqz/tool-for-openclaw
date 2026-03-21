import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-6 py-14">
      <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          OpenClaw Platform
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
          OpenClaw Skill Explorer + Risk Scanner
        </h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-slate-700">
          Discover skills faster, evaluate operational risk with confidence, and apply safer
          configuration guidance before rollout.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            href="/skills"
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
            aria-label="Browse skills"
          >
            Browse Skills
          </Link>
          <Link
            href="/scan"
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50"
            aria-label="Scan a skill"
          >
            Scan a Skill
          </Link>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900">Skill Discovery</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Search and filter curated skills by category, stars, and risk profile to find the best
            fit quickly.
          </p>
        </article>
        <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900">Risk Analysis</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Understand capability flags, risk levels, and actionable recommendations from one clear
            report card.
          </p>
        </article>
        <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-base font-semibold text-slate-900">Configuration Guidance</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Review top risk factors first and apply practical hardening steps before enabling a
            skill in production.
          </p>
        </article>
      </section>
    </main>
  );
}

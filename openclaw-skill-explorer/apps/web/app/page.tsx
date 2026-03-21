import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-8 px-6 py-14">
      <section className="rounded-xl border border-slate-200 bg-white p-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          OpenClaw Skill Explorer + Risk Scanner
        </h1>
        <p className="mt-3 text-base text-slate-700">
          Discover OpenClaw skills, review metadata, and run deterministic risk scans.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/skills"
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Browse Skills
          </Link>
          <Link
            href="/scan"
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50"
          >
            Manual Scan
          </Link>
        </div>
      </section>
      <p className="w-fit rounded-md bg-emerald-100 px-4 py-2 text-sm font-medium text-emerald-800">
        Frontend status: running
      </p>
    </main>
  );
}

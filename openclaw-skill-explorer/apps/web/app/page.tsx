export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-3xl flex-col items-center justify-center gap-4 px-6 text-center">
      <h1 className="text-3xl font-bold tracking-tight">OpenClaw Skill Explorer + Risk Scanner</h1>
      <p className="text-base text-slate-700">MVP foundation for skill discovery, evaluation, and configuration support.</p>
      <p className="rounded-md bg-emerald-100 px-4 py-2 text-sm font-medium text-emerald-800">
        Frontend status: running
      </p>
      <p className="text-sm text-slate-600">Backend integration and feature pages will be added in later rounds.</p>
    </main>
  );
}

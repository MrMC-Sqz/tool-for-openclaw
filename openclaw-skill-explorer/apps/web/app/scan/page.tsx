"use client";

import { useState } from "react";

import RiskCard from "../../components/RiskCard";
import { scanText, type RiskReport } from "../../lib/api";

export default function ManualScanPage() {
  const [inputType, setInputType] = useState<"readme" | "manifest">("readme");
  const [text, setText] = useState("");
  const [result, setResult] = useState<RiskReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async () => {
    if (!text.trim()) {
      setError("Please provide text to scan.");
      return;
    }
    setError(null);
    setIsLoading(true);
    try {
      const data = await scanText(text, inputType);
      setResult(data);
    } catch (scanError) {
      setError("Failed to run scan.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Manual Scan</h1>
      <p className="mt-1 text-sm text-slate-600">
        Paste README or manifest text to run a deterministic risk scan.
      </p>

      <section className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
        <label className="block text-sm font-medium text-slate-700">Input Type</label>
        <select
          value={inputType}
          onChange={(event) => setInputType(event.target.value as "readme" | "manifest")}
          className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
        >
          <option value="readme">README</option>
          <option value="manifest">Manifest</option>
        </select>

        <label className="mt-4 block text-sm font-medium text-slate-700">Text</label>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={12}
          className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none ring-slate-300 focus:ring-2"
          placeholder="Paste README or manifest content..."
        />

        <button
          type="button"
          onClick={handleScan}
          disabled={isLoading}
          className="mt-4 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoading ? "Scanning..." : "Scan"}
        </button>
        {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}
      </section>

      <section className="mt-6">
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Scan Result</h2>
        {result ? (
          <RiskCard
            risk_level={result.risk_level}
            risk_score={result.risk_score}
            flags={result.flags}
            reasons={result.reasons}
            recommendations={result.recommendations}
          />
        ) : (
          <p className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
            No data.
          </p>
        )}
      </section>
    </main>
  );
}


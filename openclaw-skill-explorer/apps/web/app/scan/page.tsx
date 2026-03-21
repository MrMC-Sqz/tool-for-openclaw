"use client";

import { useRef, useState } from "react";

import RiskCard from "../../components/RiskCard";
import { scanText, type RiskReport } from "../../lib/api";

export default function ManualScanPage() {
  const [inputType, setInputType] = useState<"readme" | "manifest">("readme");
  const [text, setText] = useState("");
  const [result, setResult] = useState<RiskReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const resultRef = useRef<HTMLElement | null>(null);

  const isScanDisabled = isLoading || !text.trim();

  const handleScan = async () => {
    if (!text.trim()) {
      setError("Please provide README or manifest text before scanning.");
      return;
    }
    setError(null);
    setIsLoading(true);
    try {
      const data = await scanText(text, inputType);
      setResult(data);
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 50);
    } catch (_scanError) {
      setError("Unable to run scan right now. Please check your connection and retry.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-8">
      <h1 className="text-3xl font-bold tracking-tight text-slate-900">Manual Scan</h1>
      <p className="mt-2 text-sm text-slate-600">
        Paste README or manifest content to run a deterministic risk scan and get actionable
        recommendations.
      </p>

      <section className="mt-6 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <label htmlFor="scan-input-type" className="block text-sm font-medium text-slate-700">
          Input Type
        </label>
        <select
          id="scan-input-type"
          value={inputType}
          onChange={(event) => setInputType(event.target.value as "readme" | "manifest")}
          className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900"
          aria-label="Select scan input type"
        >
          <option value="readme">README</option>
          <option value="manifest">Manifest</option>
        </select>

        <label htmlFor="scan-text" className="mt-4 block text-sm font-medium text-slate-700">
          Text
        </label>
        <textarea
          id="scan-text"
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={12}
          className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none ring-slate-300 focus:ring-2"
          placeholder="Paste README or manifest content..."
          aria-label="Scan input text"
        />

        <div className="mt-4 flex items-center gap-3">
          <button
            type="button"
            onClick={handleScan}
            disabled={isScanDisabled}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            aria-label="Run manual risk scan"
          >
            {isLoading ? "Scanning..." : "Scan"}
          </button>
          <button
            type="button"
            onClick={() => {
              setText("");
              setResult(null);
              setError(null);
            }}
            className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            aria-label="Clear scan form"
          >
            Clear
          </button>
        </div>

        {error ? (
          <div className="mt-4 rounded-md border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
            <p>{error}</p>
            <button
              type="button"
              onClick={handleScan}
              disabled={isScanDisabled}
              className="mt-2 rounded-md border border-rose-300 px-3 py-1 font-medium text-rose-700 hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-60"
              aria-label="Retry scan"
            >
              Retry
            </button>
          </div>
        ) : null}
      </section>

      <section ref={resultRef} className="mt-6">
        <h2 className="mb-3 text-xl font-semibold text-slate-900">Scan Result</h2>
        {isLoading ? (
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-600">Analyzing text...</p>
          </div>
        ) : null}
        {!isLoading && result ? (
          <RiskCard
            risk_level={result.risk_level}
            risk_score={result.risk_score}
            flags={result.flags}
            reasons={result.reasons}
            recommendations={result.recommendations}
          />
        ) : null}
        {!isLoading && !result ? (
          <div className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-600 shadow-sm">
            <p>No scan result yet.</p>
            <p className="mt-1">Enter text and click Scan to generate a risk report.</p>
          </div>
        ) : null}
      </section>
    </main>
  );
}

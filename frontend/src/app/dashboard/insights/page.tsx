"use client";

import { useEffect, useState } from "react";
import {
  Brain,
  Calendar,
  Sparkles,
  AlertTriangle,
  Lightbulb,
  TrendingUp,
  ChevronRight,
  Loader2,
  ShieldCheck,
  BarChart3,
} from "lucide-react";
import { getApiUrl } from "@/utils/config";

interface InsightReport {
  summary: string;
  insights: string[];
  alerts: string[];
  recommendations: string[];
}

interface InsightResponse {
  status: string;
  date: string;
  role: string;
  store_count: number;
  report: InsightReport;
}

export default function InsightsPage() {
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InsightResponse | null>(null);
  const [error, setError] = useState("");
  const [minDate, setMinDate] = useState<string | null>(null);
  const [maxDate, setMaxDate] = useState<string | null>(null);

  useEffect(() => {
    // Fetch available date range
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch(getApiUrl("/insights/check"), {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) return null;
        return r.json();
      })
      .then((d) => {
        if (!d) return;
        if (d.min_date) setMinDate(d.min_date);
        if (d.max_date) {
          setMaxDate(d.max_date);
          setSelectedDate(d.max_date); // default to latest
        }
      })
      .catch(() => {});
  }, []);

  const handleGenerate = async () => {
    if (!selectedDate) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("You are not logged in. Please log in again.");
        setLoading(false);
        return;
      }
      const res = await fetch(getApiUrl("/insights"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ kpi_date: selectedDate }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data?.detail || `Server error (${res.status}). Please try again.`);
        return;
      }
      setResult(data);
    } catch (e: any) {
      console.error("Insights fetch error:", e);
      setError(`Network error: ${e?.message || "Could not reach the backend."}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Header */}
      <header>
        <div className="flex items-center gap-3 mb-1">
          <div className="p-2 bg-violet-500/20 rounded-xl">
            <Brain className="w-6 h-6 text-violet-400" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">AI Insights</h1>
        </div>
        <p className="text-slate-400 ml-14">
          Role-scoped business intelligence powered by Groq LLM.
        </p>
      </header>

      {/* Date Picker Card */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
          <div className="flex-1 space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-violet-400" />
              Select KPI Date
            </label>
            <input
              type="date"
              value={selectedDate}
              min={minDate || undefined}
              max={maxDate || undefined}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-violet-500 text-sm w-full sm:w-64"
            />
            {minDate && maxDate && (
              <p className="text-xs text-slate-500">
                Available range: <span className="text-slate-400">{minDate}</span> → <span className="text-slate-400">{maxDate}</span>
              </p>
            )}
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !selectedDate}
            className="flex items-center gap-2 px-6 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl font-semibold shadow-lg shadow-violet-500/25 transition-all hover:shadow-violet-500/40 hover:-translate-y-0.5"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Generate Insights
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-300 p-4 rounded-2xl flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 mt-0.5 shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-4 animate-pulse">
          <div className="h-32 bg-slate-900/60 border border-slate-800 rounded-2xl" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="h-52 bg-slate-900/60 border border-slate-800 rounded-2xl" />
            <div className="h-52 bg-slate-900/60 border border-slate-800 rounded-2xl" />
          </div>
          <div className="h-52 bg-slate-900/60 border border-slate-800 rounded-2xl" />
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-6 animate-in fade-in duration-500">
          {/* Meta */}
          <div className="flex flex-wrap gap-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-violet-500/20 text-violet-300 border border-violet-500/30 rounded-full text-xs font-medium">
              <ShieldCheck className="w-3 h-3" /> {result.role}
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-800 text-slate-300 border border-slate-700 rounded-full text-xs font-medium">
              <Calendar className="w-3 h-3" /> {result.date}
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-800 text-slate-300 border border-slate-700 rounded-full text-xs font-medium">
              <BarChart3 className="w-3 h-3" /> {result.store_count} store{result.store_count !== 1 ? "s" : ""} analyzed
            </span>
          </div>

          {/* Summary */}
          <div className="bg-gradient-to-br from-violet-500/10 to-indigo-500/10 border border-violet-500/20 rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-violet-400 uppercase tracking-widest mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4" /> Executive Summary
            </h2>
            <p className="text-slate-200 leading-relaxed text-base">{result.report.summary}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Insights */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" /> Key Insights
              </h2>
              <ul className="space-y-3">
                {result.report.insights.map((insight, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <ChevronRight className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                    <p className="text-slate-300 text-sm leading-relaxed">{insight}</p>
                  </li>
                ))}
              </ul>
            </div>

            {/* Alerts */}
            <div className={`rounded-2xl p-6 border ${result.report.alerts.length > 0 ? "bg-amber-500/5 border-amber-500/20" : "bg-slate-900/60 border-slate-800"}`}>
              <h2 className="text-sm font-semibold text-amber-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" /> Alerts
              </h2>
              {result.report.alerts.length === 0 ? (
                <div className="flex items-center gap-3 text-emerald-400">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <p className="text-sm">No critical alerts — all systems healthy.</p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {result.report.alerts.map((alert, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" />
                      <p className="text-slate-300 text-sm leading-relaxed">{alert}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-emerald-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Lightbulb className="w-4 h-4" /> Recommendations
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {result.report.recommendations.map((rec, i) => (
                <div
                  key={i}
                  className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 flex items-start gap-3"
                >
                  <span className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold flex items-center justify-center shrink-0">
                    {i + 1}
                  </span>
                  <p className="text-slate-300 text-sm leading-relaxed">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

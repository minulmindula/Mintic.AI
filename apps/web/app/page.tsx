"use client";

import { useState } from "react";
import { ShieldCheck, ShieldAlert, TrendingUp, AlertTriangle, Cpu, DollarSign } from "lucide-react";

interface AnalysisResponse {
  status: string;
  symbol: string;
  is_approved: boolean;
  proposal?: {
    symbol: string;
    action: string;
    quantity: number;
    confidence_score: number;
    target_price: number;
    stop_loss: number;
    reasoning_summary: string;
  };
  safety_result: {
    is_approved: boolean;
    reason: string;
    failed_checks: string[];
  };
  execution_result?: {
    order_id?: string;
    status?: string;
    symbol?: string;
    error?: string;
  };
}

export default function Home() {
  const [symbol, setSymbol] = useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTrigger = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/trigger-analysis", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symbol,
          market_data: { current_price: 180.0, volume_24h: 50000000 },
          account_state: { buying_power: 25000.0, cash: 25000.0 },
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data: AnalysisResponse = await res.json();
      setResult(data);
    } catch (err: any) {
      if (err.name === "TypeError" && err.message === "Failed to fetch") {
        setError("Failed to connect to FastAPI backend at http://localhost:8000. Please make sure the server is running (`cd apps/api && uv run uvicorn src.api.main:app --port 8000`).");
      } else {
        setError(err.message || "Failed to trigger trade analysis");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen max-w-7xl mx-auto p-6 md:p-12">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
            Mintic.AI Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous Multi-Agent Trade Deliberation & Deterministic Safety Lock Engine
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex items-center space-x-3 bg-slate-900 border border-slate-800 rounded-lg px-4 py-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-xs font-semibold text-slate-300">FastAPI & Alpaca Paper Ready</span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Controls & Trigger Form */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2 mb-4">
            <Cpu className="w-5 h-5 text-blue-400" />
            Trigger Multi-Agent Analysis
          </h2>
          <form onSubmit={handleTrigger} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                Stock Symbol (GBP / Stock Whitelist)
              </label>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              >
                <option value="AAPL">AAPL - Apple Inc.</option>
                <option value="GOOGL">GOOGL - Alphabet Inc.</option>
                <option value="MSFT">MSFT - Microsoft Corp.</option>
                <option value="NVDA">NVDA - NVIDIA Corp.</option>
                <option value="AMZN">AMZN - Amazon.com Inc.</option>
                <option value="TSLA">TSLA - Tesla Inc.</option>
                <option value="META">META - Meta Platforms</option>
                <option value="SPY">SPY - S&P 500 ETF</option>
                <option value="UNAPPROVED_TICKER">UNAPPROVED_TICKER (Test Safety Lock)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold py-3 px-4 rounded-lg shadow-lg transition-all duration-200 disabled:opacity-50 flex justify-center items-center gap-2 text-sm"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Running Deliberation Graph...
                </>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4" />
                  Deliberate Trade Proposal
                </>
              )}
            </button>
          </form>

          {/* Guidelines Summary */}
          <div className="mt-8 pt-6 border-t border-slate-800/80 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Deterministic Safety Bounds (GBP)
            </h3>
            <div className="space-y-2 text-xs text-slate-400">
              <div className="flex justify-between py-1 border-b border-slate-800/40">
                <span>Max Position Size:</span>
                <span className="font-mono text-slate-200">£10,000.00</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/40">
                <span>Min Confidence Score:</span>
                <span className="font-mono text-slate-200">0.70 (70%)</span>
              </div>
              <div className="flex justify-between py-1">
                <span>Max Daily Drawdown:</span>
                <span className="font-mono text-slate-200">5.0%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Deliberation Results */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-5 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-red-300">Execution Error</h3>
                <p className="text-xs text-red-400 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!result && !loading && !error && (
            <div className="bg-slate-900/60 border border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-500">
              <Cpu className="w-10 h-10 mx-auto mb-3 opacity-40" />
              <p className="text-sm font-medium">Select a symbol and trigger trade analysis.</p>
              <p className="text-xs text-slate-600 mt-1">
                Deliberation graph will execute Analyst, Bull, Bear, and Risk Manager nodes.
              </p>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Safety Lock Status Card */}
              <div
                className={`border rounded-xl p-6 shadow-xl ${
                  result.is_approved
                    ? "bg-emerald-950/20 border-emerald-800/50"
                    : "bg-rose-950/20 border-rose-800/50"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {result.is_approved ? (
                      <ShieldCheck className="w-8 h-8 text-emerald-400" />
                    ) : (
                      <ShieldAlert className="w-8 h-8 text-rose-400" />
                    )}
                    <div>
                      <h3 className="text-base font-bold text-slate-100">
                        Safety Lock Status: {result.is_approved ? "APPROVED" : "REJECTED"}
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">{result.safety_result.reason}</p>
                    </div>
                  </div>
                  <span
                    className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider ${
                      result.is_approved
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                        : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                    }`}
                  >
                    {result.symbol}
                  </span>
                </div>

                {result.safety_result.failed_checks.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-rose-800/40">
                    <h4 className="text-xs font-semibold text-rose-300 mb-2">Violated Safety Rules:</h4>
                    <ul className="list-disc list-inside space-y-1 text-xs text-rose-400">
                      {result.safety_result.failed_checks.map((chk, i) => (
                        <li key={i}>{chk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Trade Proposal Breakdown */}
              {result.proposal && (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                  <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-emerald-400" />
                    Deliberated Trade Proposal
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                      <span className="text-xs text-slate-400 block">Action</span>
                      <span
                        className={`text-sm font-bold font-mono ${
                          result.proposal.action === "BUY" ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {result.proposal.action}
                      </span>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                      <span className="text-xs text-slate-400 block">Quantity</span>
                      <span className="text-sm font-bold font-mono text-slate-100">
                        {result.proposal.quantity}
                      </span>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                      <span className="text-xs text-slate-400 block">Target Price</span>
                      <span className="text-sm font-bold font-mono text-slate-100">
                        £{result.proposal.target_price.toFixed(2)}
                      </span>
                    </div>
                    <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                      <span className="text-xs text-slate-400 block">Confidence</span>
                      <span className="text-sm font-bold font-mono text-blue-400">
                        {(result.proposal.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-slate-800">
                    <span className="text-xs font-semibold text-slate-400 block mb-1">
                      Reasoning Summary
                    </span>
                    <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800/60">
                      {result.proposal.reasoning_summary}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

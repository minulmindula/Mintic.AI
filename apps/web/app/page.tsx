"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  TrendingUp,
  AlertTriangle,
  Cpu,
  DollarSign,
  FileText,
  TrendingDown,
  BrainCircuit,
  Activity,
  History,
  Search,
  Wallet,
  LineChart,
} from "lucide-react";
import {
  AccountSummaryResponse,
  AuditLogEntry,
  MarketQuoteResponse,
  TriggerAnalysisResponse,
} from "../../../packages/shared-types";

export default function Home() {
  const [symbol, setSymbol] = useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TriggerAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"proposal" | "deliberation" | "audit">("proposal");

  // Additional API State
  const [account, setAccount] = useState<AccountSummaryResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [quoteSymbol, setQuoteSymbol] = useState("AAPL");
  const [quote, setQuote] = useState<MarketQuoteResponse | null>(null);
  const [quoteLoading, setQuoteLoading] = useState(false);

  // Fetch Account Summary & Audit Logs on Mount
  useEffect(() => {
    fetchAccount();
    fetchAuditLogs();
  }, []);

  const fetchAccount = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/account");
      if (res.ok) {
        const data: AccountSummaryResponse = await res.json();
        setAccount(data);
      }
    } catch {
      // Ignore initial connection errors silently
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/audit-logs?limit=20");
      if (res.ok) {
        const data: AuditLogEntry[] = await res.json();
        setAuditLogs(data);
      }
    } catch {
      // Ignore initial connection errors silently
    }
  };

  const handleFetchQuote = async (e: React.FormEvent) => {
    e.preventDefault();
    setQuoteLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/market/quote/${quoteSymbol}`);
      if (res.ok) {
        const data: MarketQuoteResponse = await res.json();
        setQuote(data);
      }
    } catch {
      // Ignore quote errors
    } finally {
      setQuoteLoading(false);
    }
  };

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

      const data: TriggerAnalysisResponse = await res.json();
      setResult(data);
      // Refresh audit logs and account after triggering analysis
      fetchAuditLogs();
      fetchAccount();
    } catch (err: any) {
      if (err.name === "TypeError" && err.message === "Failed to fetch") {
        setError(
          "Failed to connect to FastAPI backend at http://localhost:8000. Please make sure the server is running (`cd apps/api && uv run uvicorn src.api.main:app --port 8000`)."
        );
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
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
            Mintic.AI Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous Multi-Agent Trade Deliberation & Deterministic Safety Lock Engine
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg p-1.5">
            <Link
              href="/"
              className="px-4 py-2 text-xs font-bold rounded-md bg-blue-600 text-white transition-colors"
            >
              Trading Dashboard
            </Link>
            <Link
              href="/charts"
              className="px-4 py-2 text-xs font-bold rounded-md text-slate-400 hover:text-slate-200 transition-colors flex items-center gap-1.5"
            >
              <LineChart className="w-3.5 h-3.5 text-emerald-400" />
              Stock Charts
            </Link>
          </div>
        </div>
      </header>

      {/* Real-Time Account Summary Banner */}
      {account && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg border border-blue-500/20 text-blue-400">
              <Wallet className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider block">
                Buying Power
              </span>
              <span className="text-lg font-bold font-mono text-slate-100">
                £{account.buying_power.toLocaleString("en-GB", { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20 text-emerald-400">
              <DollarSign className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider block">
                Portfolio Value
              </span>
              <span className="text-lg font-bold font-mono text-slate-100">
                £{account.portfolio_value.toLocaleString("en-GB", { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-indigo-500/10 rounded-lg border border-indigo-500/20 text-indigo-400">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider block">
                Open Positions
              </span>
              <span className="text-lg font-bold font-mono text-slate-100">
                {account.positions.length} Positions
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Controls & Trigger Form */}
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2 mb-4">
              <Cpu className="w-5 h-5 text-blue-400" />
              Trigger Multi-Agent Analysis
            </h2>
            <form onSubmit={handleTrigger} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                  Stock Symbol (GBP Whitelist)
                </label>
                <select
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                >
                  <optgroup label="📈 Major Stocks">
                    <option value="AAPL">AAPL - Apple Inc.</option>
                    <option value="GOOGL">GOOGL - Alphabet Inc.</option>
                    <option value="MSFT">MSFT - Microsoft Corp.</option>
                    <option value="NVDA">NVDA - NVIDIA Corp.</option>
                    <option value="AMZN">AMZN - Amazon.com Inc.</option>
                    <option value="TSLA">TSLA - Tesla Inc.</option>
                    <option value="META">META - Meta Platforms</option>
                    <option value="SPY">SPY - S&P 500 ETF</option>
                    <option value="AMD">AMD - Advanced Micro Devices</option>
                    <option value="NFLX">NFLX - Netflix Inc.</option>
                    <option value="INTC">INTC - Intel Corp.</option>
                    <option value="BABA">BABA - Alibaba Group</option>
                    <option value="COIN">COIN - Coinbase Global</option>
                    <option value="PLTR">PLTR - Palantir Tech</option>
                  </optgroup>
                  <optgroup label="🪙 Top Cryptocurrencies">
                    <option value="BTC/USD">BTC/USD - Bitcoin</option>
                    <option value="ETH/USD">ETH/USD - Ethereum</option>
                    <option value="SOL/USD">SOL/USD - Solana</option>
                    <option value="DOGE/USD">DOGE/USD - Dogecoin</option>
                    <option value="ADA/USD">ADA/USD - Cardano</option>
                    <option value="XRP/USD">XRP/USD - Ripple</option>
                    <option value="AVAX/USD">AVAX/USD - Avalanche</option>
                    <option value="DOT/USD">DOT/USD - Polkadot</option>
                    <option value="LINK/USD">LINK/USD - Chainlink</option>
                    <option value="MATIC/USD">MATIC/USD - Polygon</option>
                  </optgroup>
                  <optgroup label="🧪 Safety Lock Testing">
                    <option value="UNAPPROVED_TICKER">
                      UNAPPROVED_TICKER (Test Safety Rejection)
                    </option>
                  </optgroup>
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
          </div>

          {/* Ticker Quote Lookup Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2 mb-3">
              <Search className="w-4 h-4 text-emerald-400" />
              Live Quote Lookup (`GET /market/quote`)
            </h3>
            <form onSubmit={handleFetchQuote} className="flex gap-2 mb-3">
              <input
                type="text"
                value={quoteSymbol}
                onChange={(e) => setQuoteSymbol(e.target.value.toUpperCase())}
                placeholder="Ticker (e.g. NVDA)"
                className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              />
              <button
                type="submit"
                disabled={quoteLoading}
                className="bg-slate-800 hover:bg-slate-700 text-xs font-semibold px-3 py-2 rounded-lg text-slate-200"
              >
                Quote
              </button>
            </form>

            {quote && (
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs space-y-1 font-mono">
                <div className="flex justify-between text-slate-300">
                  <span>Price:</span>
                  <span className="text-emerald-400 font-bold">£{quote.current_price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Ask / Bid:</span>
                  <span>£{quote.ask_price.toFixed(2)} / £{quote.bid_price.toFixed(2)}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-5 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-red-300">
                  Execution Error
                </h3>
                <p className="text-xs text-red-400 mt-1">{error}</p>
              </div>
            </div>
          )}

          {!result && !loading && !error && (
            <div className="bg-slate-900/60 border border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-500">
              <Cpu className="w-10 h-10 mx-auto mb-3 opacity-40" />
              <p className="text-sm font-medium">
                Select a symbol and trigger trade analysis.
              </p>
              <p className="text-xs text-slate-600 mt-1">
                Deliberation graph will execute Analyst, Bull, Bear, and Risk
                Manager nodes.
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
                        Safety Lock Status:{" "}
                        {result.is_approved ? "APPROVED" : "REJECTED"}
                      </h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {result.safety_result.reason}
                      </p>
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
                    <h4 className="text-xs font-semibold text-rose-300 mb-2">
                      Violated Safety Rules:
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-xs text-rose-400">
                      {result.safety_result.failed_checks.map((chk, i) => (
                        <li key={i}>{chk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* View Switcher Tabs */}
              <div className="flex space-x-2 border-b border-slate-800 pb-2">
                <button
                  onClick={() => setActiveTab("proposal")}
                  className={`px-4 py-2 text-xs font-bold rounded-lg transition-all flex items-center gap-2 ${
                    activeTab === "proposal"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <DollarSign className="w-4 h-4" />
                  Trade Proposal & Execution
                </button>
                <button
                  onClick={() => setActiveTab("deliberation")}
                  className={`px-4 py-2 text-xs font-bold rounded-lg transition-all flex items-center gap-2 ${
                    activeTab === "deliberation"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <BrainCircuit className="w-4 h-4" />
                  Deliberation Reports
                </button>
                <button
                  onClick={() => setActiveTab("audit")}
                  className={`px-4 py-2 text-xs font-bold rounded-lg transition-all flex items-center gap-2 ${
                    activeTab === "audit"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-900 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <History className="w-4 h-4" />
                  Database Audit Trail (`/audit-logs`)
                </button>
              </div>

              {/* Tab 1: Trade Proposal & Execution */}
              {activeTab === "proposal" && result.proposal && (
                <div className="space-y-6">
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
                      <DollarSign className="w-5 h-5 text-emerald-400" />
                      Deliberated Trade Proposal
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                      <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                        <span className="text-xs text-slate-400 block">
                          Action
                        </span>
                        <span
                          className={`text-sm font-bold font-mono ${
                            result.proposal.action === "BUY"
                              ? "text-emerald-400"
                              : "text-rose-400"
                          }`}
                        >
                          {result.proposal.action}
                        </span>
                      </div>
                      <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                        <span className="text-xs text-slate-400 block">
                          Quantity
                        </span>
                        <span className="text-sm font-bold font-mono text-slate-100">
                          {result.proposal.quantity}
                        </span>
                      </div>
                      <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                        <span className="text-xs text-slate-400 block">
                          Target Price
                        </span>
                        <span className="text-sm font-bold font-mono text-slate-100">
                          £{result.proposal.target_price.toFixed(2)}
                        </span>
                      </div>
                      <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                        <span className="text-xs text-slate-400 block">
                          Confidence
                        </span>
                        <span className="text-sm font-bold font-mono text-blue-400">
                          {(result.proposal.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-slate-800">
                      <span className="text-xs font-semibold text-slate-400 block mb-1">
                        Reasoning Summary
                      </span>
                      <p className="text-xs text-slate-200 leading-relaxed bg-slate-950 p-4 rounded-lg border border-slate-800/80 font-mono whitespace-pre-wrap">
                        {result.proposal.reasoning_summary}
                      </p>
                    </div>
                  </div>

                  {/* Execution Output Card */}
                  {result.execution_result && (
                    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                      <h4 className="text-sm font-bold text-slate-100 mb-2 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-emerald-400" />
                        Alpaca Paper Broker Execution Status
                      </h4>
                      <pre className="text-xs text-emerald-300 bg-slate-950 p-3 rounded-lg font-mono overflow-x-auto border border-slate-800">
                        {JSON.stringify(result.execution_result, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Multi-Agent Deliberation Reports */}
              {activeTab === "deliberation" && (
                <div className="space-y-6">
                  {/* Analyst Report */}
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h4 className="text-sm font-bold text-slate-100 mb-2 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-blue-400" />
                      1. Financial Analyst Node Report
                    </h4>
                    <div className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-lg border border-slate-800 whitespace-pre-wrap font-mono">
                      {result.analyst_report || "No analyst report text returned."}
                    </div>
                  </div>

                  {/* Bull Hypothesis */}
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h4 className="text-sm font-bold text-emerald-300 mb-2 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-emerald-400" />
                      2. Bull Node Optimistic Hypothesis
                    </h4>
                    <div className="text-xs text-emerald-200/90 leading-relaxed bg-slate-950 p-4 rounded-lg border border-emerald-900/40 whitespace-pre-wrap font-mono">
                      {result.bull_hypothesis || "No bull hypothesis text returned."}
                    </div>
                  </div>

                  {/* Bear Hypothesis */}
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                    <h4 className="text-sm font-bold text-rose-300 mb-2 flex items-center gap-2">
                      <TrendingDown className="w-4 h-4 text-rose-400" />
                      3. Bear Node Risk Hypothesis
                    </h4>
                    <div className="text-xs text-rose-200/90 leading-relaxed bg-slate-950 p-4 rounded-lg border border-rose-900/40 whitespace-pre-wrap font-mono">
                      {result.bear_hypothesis || "No bear hypothesis text returned."}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 3: Historical Audit Trail Table */}
              {activeTab === "audit" && (
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                  <h4 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
                    <History className="w-4 h-4 text-blue-400" />
                    Database Audit Log History (`GET /api/v1/audit-logs`)
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                        <tr>
                          <th className="p-3">ID</th>
                          <th className="p-3">Symbol</th>
                          <th className="p-3">Approved</th>
                          <th className="p-3">Confidence</th>
                          <th className="p-3">Reasoning</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800 text-slate-300">
                        {auditLogs.map((log) => (
                          <tr key={log.id} className="hover:bg-slate-950/50">
                            <td className="p-3 text-slate-500">#{log.id}</td>
                            <td className="p-3 font-bold text-slate-100">{log.symbol}</td>
                            <td className="p-3">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                  log.is_approved
                                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                                    : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                                }`}
                              >
                                {log.is_approved ? "APPROVED" : "REJECTED"}
                              </span>
                            </td>
                            <td className="p-3 text-blue-400">
                              {(log.confidence_score * 100).toFixed(0)}%
                            </td>
                            <td className="p-3 text-slate-400 max-w-xs truncate">
                              {log.reasoning_summary}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
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

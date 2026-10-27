"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  TrendingUp,
  TrendingDown,
  Activity,
  ArrowLeft,
  Calendar,
  BarChart2,
  DollarSign,
  Maximize2,
  Compass,
  Newspaper,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import {
  MarketHistoryResponse,
  MarketQuoteResponse,
} from "../../../../packages/shared-types";

export default function ChartsPage() {
  const [symbol, setSymbol] = useState("AAPL");
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<MarketHistoryResponse | null>(null);
  const [quote, setQuote] = useState<MarketQuoteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMarketHistory(symbol, days);
    fetchQuote(symbol);
  }, [symbol, days]);

  const fetchQuote = async (targetSymbol: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/market/quote/${targetSymbol}`);
      if (res.ok) {
        const quoteRes: MarketQuoteResponse = await res.json();
        setQuote(quoteRes);
      }
    } catch {
      // Ignore quote errors
    }
  };

  const fetchMarketHistory = async (targetSymbol: string, targetDays: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/market/history/${targetSymbol}?days=${targetDays}`
      );
      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }
      const historyRes: MarketHistoryResponse = await res.json();
      setData(historyRes);
    } catch (err: any) {
      setError(
        err.message || "Failed to fetch historical market chart data from backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const candles = data?.candles || [];
  const latestPrice = candles.length > 0 ? candles[candles.length - 1].close : 0;
  const previousPrice = candles.length > 1 ? candles[0].close : latestPrice;
  const priceChange = latestPrice - previousPrice;
  const priceChangePercent = previousPrice > 0 ? (priceChange / previousPrice) * 100 : 0;

  const highestPrice = candles.length > 0 ? Math.max(...candles.map((c) => c.high)) : 0;
  const lowestPrice = candles.length > 0 ? Math.min(...candles.map((c) => c.low)) : 0;
  const avgVolume =
    candles.length > 0
      ? Math.round(candles.reduce((acc, c) => acc + c.volume, 0) / candles.length)
      : 0;

  return (
    <main className="min-h-screen max-w-7xl mx-auto p-6 md:p-12">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 pb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-100 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back to Dashboard
            </Link>
            <span className="text-xs text-slate-500">•</span>
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
              Market Analytics
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
            Stock Market Charts & Analytics
          </h1>
        </div>

        {/* Navigation Tabs */}
        <div className="mt-4 md:mt-0 flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg p-1.5">
          <Link
            href="/"
            className="px-4 py-2 text-xs font-bold rounded-md text-slate-400 hover:text-slate-200 transition-colors"
          >
            Trading Dashboard
          </Link>
          <Link
            href="/charts"
            className="px-4 py-2 text-xs font-bold rounded-md bg-blue-600 text-white transition-colors"
          >
            Stock Charts
          </Link>
        </div>
      </header>

      {/* Controls Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-8 flex flex-col md:flex-row items-center justify-between gap-4 shadow-xl">
        {/* Ticker Selector */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 shrink-0">
            Select Stock:
          </label>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm w-full md:w-64"
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
          </select>
        </div>

        {/* Timeframe Buttons */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 mr-2">
            Timeframe:
          </span>
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 text-xs font-bold rounded-lg border transition-all ${
                days === d
                  ? "bg-blue-600 border-blue-500 text-white"
                  : "bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200"
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-5 mb-8 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Financial Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">Current Price</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-slate-100">
              £{latestPrice.toFixed(2)}
            </span>
            <span
              className={`inline-flex items-center text-xs font-bold font-mono px-2 py-0.5 rounded-full ${
                priceChange >= 0
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                  : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
              }`}
            >
              {priceChange >= 0 ? "+" : ""}
              {priceChangePercent.toFixed(2)}%
            </span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">
            Period High ({days}D)
          </span>
          <span className="text-2xl font-bold font-mono text-emerald-400">
            £{highestPrice.toFixed(2)}
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">
            Period Low ({days}D)
          </span>
          <span className="text-2xl font-bold font-mono text-rose-400">
            £{lowestPrice.toFixed(2)}
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <span className="text-xs text-slate-400 block mb-1">Average Volume</span>
          <span className="text-2xl font-bold font-mono text-blue-400">
            {(avgVolume / 1000000).toFixed(2)}M
          </span>
        </div>
      </div>

      {/* Multi-Day Prediction, Investment Verdict & Google News Banner */}
      {quote && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-8 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-indigo-400" />
              <div>
                <h4 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  {symbol} Predictive Intelligence & Recommendation
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
                    Google Finance & News
                  </span>
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Algorithmic multi-day price forecast and real-time news sentiment
                </p>
              </div>
            </div>
            {quote.investment_suggestion && (
              <span
                className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider self-start sm:self-auto ${
                  quote.investment_suggestion.includes("INVEST") || quote.investment_suggestion.includes("BUY")
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                    : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                }`}
              >
                {quote.investment_suggestion.split("(")[0].trim()}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 uppercase font-semibold block mb-1">
                24h High / Low Range
              </span>
              <div className="text-xs font-mono text-slate-200">
                <span className="text-rose-400 font-bold">£{(quote.low_24h ?? lowestPrice).toFixed(2)}</span>
                <span className="text-slate-500 mx-2">—</span>
                <span className="text-emerald-400 font-bold">£{(quote.high_24h ?? highestPrice).toFixed(2)}</span>
              </div>
            </div>

            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 sm:col-span-2">
              <span className="text-[11px] text-slate-400 uppercase font-semibold block mb-1 flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5 text-blue-400" />
                Multi-Day Rise / Fall Forecast
              </span>
              <p className="text-xs font-mono text-blue-300 leading-relaxed">
                {quote.prediction || "Consolidation within expected trading channel."}
              </p>
            </div>
          </div>

          {quote.investment_suggestion && (
            <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800/80 text-xs font-mono text-slate-200 flex items-start gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 shrink-0 mt-0.5">
                Verdict:
              </span>
              <span className="font-semibold text-slate-100">
                {quote.investment_suggestion}
              </span>
            </div>
          )}

          {quote.recent_news && quote.recent_news.length > 0 && (
            <div className="pt-2 border-t border-slate-800/80 space-y-2">
              <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                <Newspaper className="w-3.5 h-3.5 text-blue-400" />
                Latest News Catalysts & Market Impact:
              </span>
              <div className="grid grid-cols-1 gap-1.5">
                {quote.recent_news.map((item, idx) => (
                  <div
                    key={idx}
                    className="text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-slate-300 font-mono leading-relaxed flex items-start gap-2"
                  >
                    <span className="text-slate-500 text-[10px] mt-0.5">•</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Interactive Charts Container */}
      <div className="space-y-8">
        {/* Price Area Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-400" />
              {symbol} Price Series (£ GBP) - {days} Days History
            </h3>
            {loading && (
              <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            )}
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={candles}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="timestamp"
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  domain={["auto", "auto"]}
                  tickFormatter={(val) => `£${val}`}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#090d16",
                    borderColor: "#334155",
                    borderRadius: "8px",
                    color: "#f8fafc",
                    fontSize: "12px",
                    fontFamily: "monospace",
                  }}
                  formatter={(value: any) => [`£${Number(value).toFixed(2)}`, "Price"]}
                />
                <Area
                  type="monotone"
                  dataKey="close"
                  stroke="#3b82f6"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#priceGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Volume Bar Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <h3 className="text-base font-bold text-slate-100 mb-6 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-emerald-400" />
            Trading Volume Breakdown
          </h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={candles}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  dataKey="timestamp"
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                />
                <YAxis
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(val) => `${(val / 1000000).toFixed(0)}M`}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#090d16",
                    borderColor: "#334155",
                    borderRadius: "8px",
                    color: "#f8fafc",
                    fontSize: "12px",
                    fontFamily: "monospace",
                  }}
                  formatter={(value: any) => [
                    `${(Number(value) / 1000000).toFixed(2)}M units`,
                    "Volume",
                  ]}
                />
                <Bar dataKey="volume" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </main>
  );
}

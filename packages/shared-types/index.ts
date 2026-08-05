/**
 * Shared TypeScript types matching Pydantic schemas in src/core/schemas.py & src/api/main.py
 */

export type TradeAction = 'BUY' | 'SELL';

export interface TradeProposal {
  symbol: string;
  action: TradeAction;
  quantity: number;
  confidence_score: number;
  target_price: number;
  stop_loss: number;
  reasoning_summary: string;
}

export interface SafetyCheckResult {
  is_approved: boolean;
  reason: string;
  proposal: TradeProposal;
  failed_checks: string[];
}

export interface TriggerAnalysisRequest {
  symbol: string;
  market_data?: Record<string, any>;
  account_state?: Record<string, any>;
}

export interface TriggerAnalysisResponse {
  status: string;
  symbol: string;
  is_approved: boolean;
  proposal?: TradeProposal;
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
  analyst_report?: string;
  bull_hypothesis?: string;
  bear_hypothesis?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  database: string;
}

export interface SafetyRulesResponse {
  allowed_symbols: string[];
  max_position_size_gbp: number;
  min_confidence_threshold: number;
  max_daily_drawdown_percent: number;
}

export interface AuditLogEntry {
  id: number;
  symbol: string;
  confidence_score: number;
  is_approved: boolean;
  reasoning_summary: string;
  created_at: string;
}

export interface AccountSummaryResponse {
  buying_power: number;
  cash: number;
  portfolio_value: number;
  currency: string;
  positions: Array<Record<string, any>>;
}

export interface MarketQuoteResponse {
  symbol: string;
  current_price: number;
  ask_price: number;
  bid_price: number;
}

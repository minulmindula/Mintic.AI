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
}

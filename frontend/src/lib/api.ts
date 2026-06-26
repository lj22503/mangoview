const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8003'
const isDev = process.env.NODE_ENV === 'development'

interface ApiResponse<T> {
  code: number
  data: T
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  })

  if (!res.ok) {
    const msg = `API error: ${res.status} ${res.statusText} [${endpoint}]`
    if (isDev) console.warn(msg)
    throw new Error(msg)
  }

  let json: ApiResponse<T>
  try {
    json = await res.json()
  } catch {
    throw new Error(`Invalid JSON response from ${endpoint}`)
  }

  return json.data
}

// === Market API ===

export interface MacroIndicator {
  name: string
  current: number | null
  previous: number | null
  direction: string
  percentile: number | null
  date: string
  source: string
  available: boolean
}

export interface MacroData {
  indicators: MacroIndicator[]
  updated_at: string
}

export interface Industry {
  code: string
  name: string
  cycle_stage: string
  penetration: number
  cr3: number
  pe_percentile: number
  net_profit_growth: number
  weight: number
}

export interface IndustryData {
  industries: Industry[]
  updated_at: string
}

export interface NorthMoneyData {
  date: string
  net_buy: number
  buy_amount: number
  sell_amount: number
  cumulative_net_buy: number
  hs300_change: number
  updated_at: string
}

export async function getMacroData(): Promise<MacroData> {
  return fetchApi<MacroData>('/v1/market/macro')
}

export async function getNorthMoney(): Promise<NorthMoneyData> {
  return fetchApi<NorthMoneyData>('/v1/market/north-money')
}

export async function getIndustries(): Promise<IndustryData> {
  return fetchApi<IndustryData>('/v1/market/industries')
}

// === Portfolio API ===

export interface PortfolioRequest {
  risk_profile: 'conservative' | 'balanced' | 'aggressive'
  time_horizon: string
  investable_amount: number
  familiar_industries: string[]
}

export interface PortfolioData {
  strategy: {
    logic: string
    allocation: Record<string, { value: number; locked: boolean; display: string }>
  }
  tactics: {
    logic: string
    targets: { locked: boolean }
  }
  requires_subscription: boolean
}

export async function postPortfolioGenerate(data: PortfolioRequest): Promise<PortfolioData> {
  return fetchApi<PortfolioData>('/v1/portfolio/generate', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

// === Analysis API ===

export interface EngineCycleResponse {
  cycle_position: {
    kitchin: string
    juglar: string
    kuznets: string
    kondratieff: string
  }
  allocation_suggestion: {
    equity: string
    bond: string
    gold: string
    cash: string
  }
  historical_comparison: { period: string; similarity: number }[]
  exit_signals: { signal: string; observable: boolean; trigger_action: string }[]
  scenario: {
    base: string
    bull: string
    bear: string
  }
  engine_result: {
    completed: boolean
    fallback?: boolean
    cycle_phase: string
    direction: string
    intensity: string
    logic: string
    confidence: number
  }
  macro_data_preview: Record<string, number | string>
}

export interface AnalysisCycleRequest {
  indicators: {
    pmi?: number
    ppi?: number
    fixed_asset_investment?: number
    new_start_area?: number
  }
}

export async function postAnalysisCycleLocator(data: AnalysisCycleRequest): Promise<EngineCycleResponse> {
  return fetchApi<EngineCycleResponse>('/v1/analysis/cycle-locator', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export interface MacroDataResponse {
  market_indices: Record<string, { current: number; change_pct: number }>
  macro_data: Record<string, number | string>
  data_source: string
  data_freshness: string
}

export async function getAnalysisMacroData(): Promise<MacroDataResponse> {
  return fetchApi<MacroDataResponse>('/v1/analysis/macro-data')
}

// === Reports API ===

export interface Report {
  id: string
  type: string
  date: string
  title: string
  summary: string
  is_locked: boolean
}

export interface ReportListData {
  reports: Report[]
  total: number
  page: number
  limit: number
}

export async function getReports(type: string = 'daily', page: number = 1, limit: number = 10): Promise<ReportListData> {
  return fetchApi<ReportListData>(`/v1/reports?type=${type}&page=${page}&limit=${limit}`)
}

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# === Macro Indicators ===

class MacroIndicator(BaseModel):
    name: str
    current: float
    previous: float
    direction: str  # up/down/flat
    percentile: float
    date: str
    source: str


class MacroDataResponse(BaseModel):
    code: int = 0
    data: dict


# === Industry ===

class Industry(BaseModel):
    code: str
    name: str
    cycle_stage: str
    penetration: float
    cr3: float
    pe_percentile: float
    net_profit_growth: float
    weight: float


class IndustryDataResponse(BaseModel):
    code: int = 0
    data: dict


# === Opportunities ===

class Opportunity(BaseModel):
    id: str
    name: str
    score: int
    trigger_level: str
    conditions: str
    suggested_position: float
    status: str


class OpportunityResponse(BaseModel):
    code: int = 0
    data: dict


# === Portfolio ===

class PortfolioRequest(BaseModel):
    risk_profile: str  # conservative/balanced/aggressive
    time_horizon: str  # 1-3骞?3-5骞?5骞翠互涓?    investable_amount: float
    familiar_industries: List[str]


class PortfolioResponse(BaseModel):
    code: int = 0
    data: dict


# === Reports ===

class Report(BaseModel):
    id: str
    type: str  # daily/weekly/monthly
    date: str
    title: str
    summary: str
    is_locked: bool


class ReportListResponse(BaseModel):
    code: int = 0
    data: dict


# === Health ===

class HealthResponse(BaseModel):
    status: str
    service: str

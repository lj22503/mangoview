from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class MacroIndicator(Base):
    __tablename__ = 'macro_indicators'

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_name = Column(String(50))  # 基钦/朱格拉/库兹涅茨/康波
    indicator_code = Column(String(50))  # PMI/PPI/固定资产投资/新开工面积
    current_value = Column(Float)
    previous_value = Column(Float)
    direction = Column(String(10))  # up/down/flat
    historical_percentile = Column(Float)  # 0-100
    data_date = Column(Date)
    source = Column(String(100))
    updated_at = Column(DateTime, default=datetime.utcnow)


class IndustryInfo(Base):
    __tablename__ = 'industry_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_code = Column(String(20), unique=True)
    industry_name = Column(String(100))
    cycle_stage = Column(String(50))
    penetration = Column(Float)
    cr3 = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)


class IndustryFinancials(Base):
    __tablename__ = 'industry_financials'

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_code = Column(String(20))
    year = Column(Integer)
    quarter = Column(Integer)
    net_profit_growth = Column(Float)
    revenue_growth = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index('idx_industry_financials', 'industry_code', 'year', 'quarter'),)


class IndustryValuation(Base):
    __tablename__ = 'industry_valuation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_code = Column(String(20))
    stat_date = Column(Date)
    pe_ttm = Column(Float)
    pe_percentile = Column(Float)
    pb_lf = Column(Float)
    pb_percentile = Column(Float)
    dividend_yield = Column(Float)
    dividend_percentile = Column(Float)
    quadrant = Column(String(50))
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index('idx_industry_valuation', 'industry_code', 'stat_date'),)


class StrategicAllocation(Base):
    __tablename__ = 'strategic_allocation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_class = Column(String(50))  # 股票/债券/黄金/现金
    target_ratio = Column(Float)  # 0-1
    risk_profile = Column(String(20))  # conservative/balanced/aggressive
    updated_at = Column(DateTime, default=datetime.utcnow)


class TacticalHolding(Base):
    __tablename__ = 'tactical_holdings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_code = Column(String(20))
    target_ratio = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Opportunity(Base):
    __tablename__ = 'opportunities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    score = Column(Integer)  # 0-25
    trigger_level = Column(String(20))  # none/level1/level2/level3
    conditions = Column(Text)
    suggested_position = Column(Float)  # 0-1
    tools_used = Column(Text)
    status = Column(String(20))  # active/expired/watching
    updated_at = Column(DateTime, default=datetime.utcnow)


class DisciplineCheck(Base):
    __tablename__ = 'discipline_checks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    check_date = Column(Date)
    score = Column(Float)
    findings = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)


class NorthMoneyFlow(Base):
    __tablename__ = 'north_money_flow'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    net_buy = Column(Float)
    buy_amount = Column(Float)
    sell_amount = Column(Float)
    cumulative_net_buy = Column(Float)
    hs300_change = Column(Float)
    source = Column(String(100))
    updated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index('idx_north_money_flow', 'date'),)


# === DB Helpers ===

DATABASE_URL = "sqlite:///C:/tmp/mangoview/data/mangoview.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
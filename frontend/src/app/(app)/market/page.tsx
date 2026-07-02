'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getMacroData, getNorthMoney, getIndustries, MacroData, NorthMoneyData, IndustryData } from '@/lib/api'

const TOP_INDICATORS = ['GDP增速', 'CPI', 'PPI', '制造业PMI', 'M2增速', '社融增量', '社零增速', '出口增速', '固投增速']

export default function MarketPage() {
  const [macro, setMacro] = useState<MacroData | null>(null)
  const [northMoney, setNorthMoney] = useState<NorthMoneyData | null>(null)
  const [industries, setIndustries] = useState<IndustryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = () => {
    setLoading(true)
    setError(null)
    Promise.all([getMacroData(), getNorthMoney(), getIndustries()])
      .then(([m, n, i]) => { setMacro(m); setNorthMoney(n); setIndustries(i) })
      .catch(e => setError(e?.message || '数据加载失败'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchData() }, [])

  const find = (name: string) => macro?.indicators.find(i => i.name === name)
  const dir = (d: string | undefined) => d === 'up' ? '↑' : d === 'down' ? '↓' : '—'
  const dirCls = (d: string | undefined) => d === 'up' ? 'text-success' : d === 'down' ? 'text-danger' : 'text-text-muted'

  const top3 = industries?.industries
    ? [...industries.industries].sort((a, b) => b.net_profit_growth - a.net_profit_growth).slice(0, 3)
    : []

  const bottom3 = industries?.industries
    ? [...industries.industries].sort((a, b) => a.net_profit_growth - b.net_profit_growth).slice(0, 3)
    : []

  // 只显示可用的指标
  const availableIndicators = TOP_INDICATORS
    .map(name => find(name))
    .filter((ind): ind is NonNullable<typeof ind> => ind != null && ind.available !== false)

  return (
    <div className="min-h-screen bg-surface-alt">
      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* Hero */}
        <div className="mb-10">
          <h1 className="text-[36px] leading-[1.15] font-bold text-text-primary tracking-hero">
            不看盘的人在看什么
          </h1>
          <p className="text-[16px] text-text-secondary mt-3 leading-relaxed">
            他们不看K线，他们看周期在哪、钱往哪跑、什么信号在发酵。
          </p>
        </div>

        {/* ===== 顶部定调：宏观快照 ===== */}
        <section className="mb-10">
          <div className="rounded-xl border border-border bg-surface p-6">
            {loading ? (
              <div className="text-center py-4 text-text-muted text-sm">加载中...</div>
            ) : macro && availableIndicators.length > 0 ? (
              <>
                <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                  {availableIndicators.map(ind => {
                    return (
                      <div key={ind.name} className="text-center">
                        <p className="text-xs text-text-muted mb-1">{ind.name}</p>
                        <p className="text-lg font-semibold text-text-primary">
                          {ind.current ?? '—'}
                          <span className={`ml-1 text-sm ${dirCls(ind.direction)}`}>
                            {dir(ind.direction)}
                          </span>
                        </p>
                        <p className="text-[11px] text-text-muted mt-0.5">
                          {ind.date ? `数据 ${ind.date.slice(0, 7)}` : ''}
                        </p>
                      </div>
                    )
                  })}
                </div>
                <div className="mt-4 pt-3 border-t border-border-light text-xs text-text-muted">
                  数据来源：{macro.indicators[0]?.source || '东方财富/国家统计局'}
                </div>
              </>
            ) : (
              <div className="text-center py-4 text-text-muted text-sm">数据加载失败</div>
            )}
          </div>
        </section>

        {/* ===== 三个数据锚点卡 ===== */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">

          {/* 周期定位 */}
          <Link
            href="/market/cycle"
            className="card group hover:-translate-y-1 hover:border-mango-400 transition-all duration-200 p-5 flex flex-col"
          >
            <h2 className="text-h2 text-text-primary mb-3 group-hover:text-mango-600 transition-colors">
              现在是什么周期？
            </h2>
            {error ? (
              <div className="text-xs text-danger py-4 flex-1">
                {error}
                <button onClick={fetchData} className="ml-2 text-mango-600 hover:underline">重试</button>
              </div>
            ) : loading ? (
              <div className="text-xs text-text-muted py-4 flex-1">加载中...</div>
            ) : macro ? (
              <div className="space-y-2 mb-3 flex-1">
                {['PMI', 'GDP', 'PPI'].map(name => {
                  const ind = find(name)
                  if (!ind) return null
                  return (
                    <div key={name} className="flex justify-between text-sm">
                      <span className="text-text-muted">{name}</span>
                      <span className="text-text-primary font-medium">
                        {ind.current}{name === 'GDP' ? '%' : ''}
                        <span className={`ml-1 ${dirCls(ind.direction)}`}>{dir(ind.direction)}</span>
                      </span>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-xs text-text-muted py-4 flex-1">北向数据暂不可用</div>
            )}
            <div className="mt-auto pt-3 border-t border-border-light flex justify-between items-center">
              <span className="text-xs text-mango-600 font-medium">查看完整定位</span>
              <span className="text-xs text-text-muted">→</span>
            </div>
          </Link>

          {/* 行业大图 */}
          <Link
            href="/market/industry"
            className="card group hover:-translate-y-1 hover:border-mango-400 transition-all duration-200 p-5 flex flex-col"
          >
            <h2 className="text-h2 text-text-primary mb-3 group-hover:text-mango-600 transition-colors">
              钱在往哪跑？
            </h2>
            {error ? (
              <div className="text-xs text-danger py-4 flex-1">
                {error}
                <button onClick={fetchData} className="ml-2 text-mango-600 hover:underline">重试</button>
              </div>
            ) : loading ? (
              <div className="text-xs text-text-muted py-4 flex-1">加载中...</div>
            ) : industries && top3.length > 0 ? (
              <div className="space-y-2 mb-3 flex-1">
                <p className="text-xs text-text-muted mb-1">增速前三</p>
                {top3.map(ind => (
                  <div key={ind.code} className="flex justify-between text-sm">
                    <span className="text-text-primary">{ind.name}</span>
                    <span className="text-success font-medium">+{ind.net_profit_growth}%</span>
                  </div>
                ))}
                {bottom3.length > 0 && (
                  <>
                    <p className="text-xs text-text-muted mb-1 mt-2">增速后三</p>
                    {bottom3.map(ind => (
                      <div key={ind.code} className="flex justify-between text-sm">
                        <span className="text-text-primary">{ind.name}</span>
                        <span className={`font-medium ${ind.net_profit_growth >= 0 ? 'text-text-secondary' : 'text-danger'}`}>
                          {ind.net_profit_growth >= 0 ? '+' : ''}{ind.net_profit_growth}%
                        </span>
                      </div>
                    ))}
                  </>
                )}
              </div>
            ) : (
              <div className="text-xs text-text-muted py-4 flex-1">暂无行业数据</div>
            )}
            <div className="mt-auto pt-3 border-t border-border-light flex justify-between items-center">
              <span className="text-xs text-mango-600 font-medium">查看行业全景</span>
              <span className="text-xs text-text-muted">→</span>
            </div>
          </Link>

          {/* 机会扫描 */}
          <Link
            href="/market/events"
            className="card group hover:-translate-y-1 hover:border-mango-400 transition-all duration-200 p-5 flex flex-col"
          >
            <h2 className="text-h2 text-text-primary mb-3 group-hover:text-mango-600 transition-colors">
              什么信号在发酵？
            </h2>
            {loading ? (
              <div className="text-xs text-text-muted py-4 flex-1">加载中...</div>
            ) : northMoney ? (
              <div className="space-y-2 mb-3 flex-1">
                <div className="flex justify-between text-sm">
                  <span className="text-text-muted">北向{(northMoney.net_buy ?? 0) >= 0 ? '净买' : '净卖'}</span>
                  <span className={`font-medium ${(northMoney.net_buy ?? 0) >= 0 ? 'text-success' : 'text-danger'}`}>
                    {(northMoney.net_buy ?? 0) >= 0 ? '+' : ''}{northMoney.net_buy ?? '—'}亿
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-muted">沪深300</span>
                  <span className={`font-medium ${(northMoney.hs300_change ?? 0) >= 0 ? 'text-success' : 'text-danger'}`}>
                    {(northMoney.hs300_change ?? 0) >= 0 ? '+' : ''}{northMoney.hs300_change ?? '—'}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-muted">累计净买</span>
                  <span className="text-text-primary font-medium">
                    {northMoney.available !== false && northMoney.cumulative_net_buy != null
                      ? `${northMoney.cumulative_net_buy.toFixed(0)}亿`
                      : '—'}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-xs text-text-muted py-4 flex-1">北向数据暂不可用</div>
            )}
            <div className="mt-auto pt-3 border-t border-border-light flex justify-between items-center">
              <span className="text-xs text-mango-600 font-medium">查看信号扫描</span>
              <span className="text-xs text-text-muted">→</span>
            </div>
          </Link>
        </div>

        {/* 合规声明 */}
        <p className="text-xs text-text-muted text-center">
          本平台仅提供投资框架与数据参考，不构成任何投资建议。市场有风险，投资需谨慎。请独立判断并自行承担风险。
        </p>

      </main>
    </div>
  )
}

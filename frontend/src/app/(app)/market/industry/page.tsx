'use client'

import { useEffect, useState } from 'react'
import { getIndustries, getMacroData, IndustryData, MacroData } from '@/lib/api'

export default function IndustryPage() {
  const [industries, setIndustries] = useState<IndustryData | null>(null)
  const [macro, setMacro] = useState<MacroData | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedIndustry, setSelectedIndustry] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([getIndustries(), getMacroData()])
      .then(([ind, m]) => { setIndustries(ind); setMacro(m) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const selectedData = industries?.industries.find(i => i.name === selectedIndustry)

  const topGrowers = industries?.industries
    ? [...industries.industries].sort((a, b) => b.net_profit_growth - a.net_profit_growth).slice(0, 3)
    : []
  const bottomGrowers = industries?.industries
    ? [...industries.industries].sort((a, b) => a.net_profit_growth - b.net_profit_growth).slice(0, 3)
    : []

  const pmiInd = macro?.indicators.find(i => i.name === 'PMI')

  return (
    <div className="min-h-screen bg-surface-alt">
      <main className="max-w-5xl mx-auto px-6 py-12">

        <section className="mb-10">
          <div className="flex items-start gap-4 mb-5">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500 text-white text-base font-bold">
              1
            </span>
            <div>
              <h1 className="text-[32px] leading-[1.15] font-bold text-text-primary tracking-hero">
                不让感觉替你选行业。
              </h1>
              <p className="text-text-secondary text-[16px] mt-1 max-w-2xl leading-relaxed">
                31 个申万一级行业，估值分位 vs 净利润增速四象限定位。
                {pmiInd && (
                  <span className="text-mango-600 font-medium"> 当前 PMI {pmiInd.current}，位于景气区间上方。</span>
                )}
              </p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <div className="flex items-start gap-4 mb-6">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500/20 text-mango-600 text-base font-bold">
              2
            </span>
            <h2 className="text-[28px] leading-[1.15] font-bold text-text-primary tracking-title">估值 vs 景气度</h2>
          </div>

          {loading ? (
            <div className="text-center py-12 text-text-muted text-sm">加载中...</div>
          ) : industries ? (
            <div className="rounded-xl border border-border bg-surface p-6">
              <div className="relative h-80 rounded-lg bg-surface-alt border border-border-light mb-4">
                <div className="absolute top-3 left-1/2 -translate-x-1/2 text-xs text-text-muted">高估值</div>
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 text-xs text-text-muted">低估值</div>
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-text-muted" style={{ writingMode: 'vertical-rl' }}>高增速</div>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-text-muted" style={{ writingMode: 'vertical-rl' }}>低增速</div>

                <div className="absolute left-1/2 top-0 bottom-0 w-px bg-border-light" />
                <div className="absolute top-1/2 left-0 right-0 h-px bg-border-light" />

                {industries.industries.map((ind, i) => {
                  const x = ind.pe_percentile
                  const y = 100 - Math.max(0, Math.min(100, ind.net_profit_growth + 50))
                  const size = Math.max(8, Math.min(20, (ind.weight || 1) * 8))
                  const isSelected = selectedIndustry === ind.name
                  return (
                    <button
                      key={i}
                      onClick={() => setSelectedIndustry(isSelected ? null : ind.name)}
                      className={`absolute rounded-full transition-all cursor-pointer hover:scale-150 ${
                        isSelected ? 'bg-mango-500 ring-2 ring-mango-300 scale-125 z-10' : 'bg-mango-500/70'
                      }`}
                      style={{
                        left: `${x}%`,
                        top: `${y}%`,
                        width: `${size}px`,
                        height: `${size}px`,
                      }}
                      title={`${ind.name}: PE${ind.pe_percentile}% 增速${ind.net_profit_growth}% ${ind.cycle_stage}`}
                    />
                  )
                })}
              </div>
              <p className="text-xs text-text-muted text-center">
                点击气泡查看详情 · X轴: PE分位 · Y轴: 净利润增速 · 气泡大小: 行业权重
              </p>
            </div>
          ) : (
            <div className="text-center py-12 text-text-muted text-sm">数据加载失败</div>
          )}
        </section>

        {selectedIndustry && selectedData && (
          <section className="mb-10">
            <div className="rounded-xl border-2 border-mango-400 bg-surface p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-h3 text-text-primary">
                  {selectedIndustry}
                  <span className="text-text-secondary text-base font-normal ml-2">
                    当前阶段：{selectedData.cycle_stage}
                  </span>
                </h3>
                <button onClick={() => setSelectedIndustry(null)} className="text-text-muted hover:text-text-primary text-lg leading-none">&times;</button>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="rounded-lg bg-surface-alt p-3">
                  <p className="text-xs text-text-muted mb-1">PE分位</p>
                  <p className="text-lg font-semibold text-text-primary">{selectedData.pe_percentile}%</p>
                </div>
                <div className="rounded-lg bg-surface-alt p-3">
                  <p className="text-xs text-text-muted mb-1">净利润增速</p>
                  <p className={`text-lg font-semibold ${selectedData.net_profit_growth >= 0 ? 'text-success' : 'text-danger'}`}>
                    {selectedData.net_profit_growth >= 0 ? '+' : ''}{selectedData.net_profit_growth}%
                  </p>
                </div>
                <div className="rounded-lg bg-surface-alt p-3">
                  <p className="text-xs text-text-muted mb-1">渗透率</p>
                  <p className="text-lg font-semibold text-text-primary">{selectedData.penetration}%</p>
                </div>
                <div className="rounded-lg bg-surface-alt p-3">
                  <p className="text-xs text-text-muted mb-1">CR3</p>
                  <p className="text-lg font-semibold text-text-primary">{(selectedData.cr3 * 100).toFixed(0)}%</p>
                </div>
              </div>
            </div>
          </section>
        )}

        <section className="mb-10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-xl border border-border bg-surface p-5">
              <h3 className="text-sm font-semibold text-success mb-3">增速领涨</h3>
              {loading ? (
                <div className="text-xs text-text-muted py-2">加载中...</div>
              ) : topGrowers.length > 0 ? (
                <div className="space-y-2">
                  {topGrowers.map(ind => (
                    <div key={ind.code} className="flex justify-between text-sm">
                      <span className="text-text-primary">{ind.name}</span>
                      <span className="text-success font-medium">+{ind.net_profit_growth}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-text-muted py-2">暂无数据</div>
              )}
            </div>
            <div className="rounded-xl border border-border bg-surface p-5">
              <h3 className="text-sm font-semibold text-danger mb-3">增速领跌</h3>
              {loading ? (
                <div className="text-xs text-text-muted py-2">加载中...</div>
              ) : bottomGrowers.length > 0 ? (
                <div className="space-y-2">
                  {bottomGrowers.map(ind => (
                    <div key={ind.code} className="flex justify-between text-sm">
                      <span className="text-text-primary">{ind.name}</span>
                      <span className={`font-medium ${ind.net_profit_growth >= 0 ? 'text-text-secondary' : 'text-danger'}`}>
                        {ind.net_profit_growth >= 0 ? '+' : ''}{ind.net_profit_growth}%
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-text-muted py-2">暂无数据</div>
              )}
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-xl font-semibold text-text-primary mb-4">行业数据</h2>
          <div className="rounded-xl border border-border bg-surface overflow-hidden">
            {loading ? (
              <div className="text-center py-12 text-text-muted text-sm">加载中...</div>
            ) : industries ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border-light">
                      <th className="text-left px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">行业</th>
                      <th className="text-left px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">周期阶段</th>
                      <th className="text-right px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">渗透率</th>
                      <th className="text-right px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">CR3</th>
                      <th className="text-right px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">PE分位</th>
                      <th className="text-right px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">净利润增速</th>
                    </tr>
                  </thead>
                  <tbody>
                    {industries.industries.map((ind, i) => (
                      <tr key={i} className="border-t border-border-light hover:bg-surface-warm cursor-pointer transition-colors"
                        onClick={() => setSelectedIndustry(selectedIndustry === ind.name ? null : ind.name)}>
                        <td className="px-5 py-3 text-sm font-medium text-text-primary">{ind.name}</td>
                        <td className="px-5 py-3 text-sm text-text-secondary">{ind.cycle_stage}</td>
                        <td className="px-5 py-3 text-right text-sm text-text-secondary">{ind.penetration}%</td>
                        <td className="px-5 py-3 text-right text-sm text-text-secondary">{(ind.cr3 * 100).toFixed(0)}%</td>
                        <td className="px-5 py-3 text-right text-sm text-text-secondary">{ind.pe_percentile}%</td>
                        <td className={`px-5 py-3 text-right text-sm font-medium ${ind.net_profit_growth >= 0 ? 'text-success' : 'text-danger'}`}>
                          {ind.net_profit_growth >= 0 ? '+' : ''}{ind.net_profit_growth}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className="px-5 py-3 text-xs text-text-muted border-t border-border-light">
                  覆盖申万 31 个一级行业 · 财务数据季度更新 · 估值数据月度更新
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-text-muted text-sm">数据加载失败</div>
            )}
          </div>
        </section>



        <section className="mb-10">
          <details className="rounded-xl border border-border bg-surface p-5 group">
            <summary className="cursor-pointer text-sm font-medium text-text-primary list-none flex items-center justify-between">
              每个指标是什么意思？
              <span className="text-xs text-text-muted group-open:hidden">展开</span>
              <span className="text-xs text-text-muted hidden group-open:inline">收起</span>
            </summary>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                { label: 'PE分位', desc: '当前估值在过去 5 年中的位置。越低越便宜。' },
                { label: '净利润增速', desc: '行业整体利润在增长还是下滑。' },
                { label: '渗透率', desc: '产品/服务在目标市场中的普及程度。低渗透 = 还有空间。' },
                { label: 'CR3', desc: '前三大公司的市场份额。越高越集中，龙头越强。' },
                { label: '周期阶段', desc: '行业处于导入/成长/成熟/衰退哪个阶段。' },
                { label: '行业权重', desc: '在整体经济中的占比，决定气泡大小。' },
                { label: '营收 TTM', desc: '过去 12 个月的行业总营收。看规模。' },
                { label: 'ROE', desc: '净资产收益率。钱生钱的本事。' },
                { label: '毛利率', desc: '卖东西能留多少利润。越高护城河越深。' },
                { label: '存货周转', desc: '货卖得快不快。周转快说明需求好。' },
                { label: 'PE_TTM', desc: '当前股价对应过去 12 个月利润的倍数。' },
                { label: '股息率', desc: '每年分红占股价的比例。稳不稳定看这个。' },
              ].map(item => (
                <div key={item.label} className="rounded-lg bg-surface-alt p-3">
                  <p className="text-sm font-medium text-text-primary mb-1">{item.label}</p>
                  <p className="text-xs text-text-secondary">{item.desc}</p>
                </div>
              ))}
            </div>
          </details>
        </section>

        <div className="text-center text-xs text-text-muted py-4 border-t border-border-light">
          本页面仅展示行业统计数据，不构成任何投资建议。行业阶段与排名为框架方法论输出，不代表对未来走势的预测。
        </div>

      </main>
    </div>
  )
}

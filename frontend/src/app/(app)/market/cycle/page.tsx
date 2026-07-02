'use client'

import { useEffect, useState } from 'react'
import { getMacroData, MacroData } from '@/lib/api'

interface CycleInfo {
  name: string
  period: string
  indicators: string[]
  currentData: { label: string; value: string }[]
  percentile: number
  historyNote: string
}

export default function CyclePage() {
  const [macro, setMacro] = useState<MacroData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMacroData().then(setMacro).catch(console.error).finally(() => setLoading(false))
  }, [])

  const find = (name: string) => macro?.indicators.find(i => i.name === name)

  const cycles: CycleInfo[] = [
    {
      name: '基钦周期',
      period: '3–4 年',
      indicators: ['PMI', 'PPI', '库存同比'],
      currentData: [
        { label: 'PMI', value: find('PMI') ? String(find('PMI')!.current) : '—' },
        { label: 'PPI', value: find('PPI') ? String(find('PPI')!.current) : '—' },
        { label: '库存', value: find('库存同比') ? String(find('库存同比')!.current) : '—' },
      ],
      percentile: find('PMI')?.percentile ?? 0,
      historyNote: '短周期供需波动，货多降价清仓、货少涨价补库，PMI 是温度计',
    },
    {
      name: '朱格拉周期',
      period: '7–11 年',
      indicators: ['高技术投资增速', '固投增速'],
      currentData: [
        { label: '高技术投资', value: find('高技术投资增速') ? String(find('高技术投资增速')!.current) : '—' },
        { label: '固投', value: find('固定资产投资') ? String(find('固定资产投资')!.current) : '—' },
      ],
      percentile: find('固定资产投资')?.percentile ?? 0,
      historyNote: '设备更新与产能替换，新旧动能交替期，看高技术投资占比',
    },
    {
      name: '库兹涅茨周期',
      period: '15–20 年',
      indicators: ['新开工面积', '销售面积'],
      currentData: [
        { label: '新开工', value: find('新开工面积') ? String(find('新开工面积')!.current) : '—' },
        { label: '销售面积', value: find('销售面积') ? String(find('销售面积')!.current) : '—' },
      ],
      percentile: find('新开工面积')?.percentile ?? 0,
      historyNote: '地产大周期，牵动上下游几十个行业，看新开工触底信号',
    },
    {
      name: '康波周期',
      period: '50–60 年',
      indicators: ['全要素生产率', 'AI渗透率'],
      currentData: [
        { label: 'TFP', value: '超长期指标' },
        { label: 'AI渗透', value: '导入期' },
      ],
      percentile: 0,
      historyNote: '技术革命周期：蒸汽机→电力→互联网→AI，一辈子只经历一次切换',
    },
  ]

  // macroRows: 指标由 API 的 available 字段决定是否显示真实数据
  const macroUnits: Record<string, string> = {
    'GDP': '%', 'CPI': '%', 'PPI': '%', 'PMI': '', 'M2': '%',
    '社融': '亿', '社零': '%', '出口': '%', '固投': '%',
  }
  const macroRows = [
    { key: 'GDP', label: 'GDP 实际增速', explain: '经济在不在长，5% 算正常' },
    { key: 'CPI', label: 'CPI', explain: '物价涨了没' },
    { key: 'PPI', label: 'PPI', explain: '企业好不好过，负数意味原材料便宜但利润薄' },
    { key: 'PMI', label: '制造业 PMI', explain: '制造业温度计，50 以上 = 景气' },
    { key: 'M2', label: 'M2 增速', explain: '市场上钱多不多' },
    { key: '社融', label: '社融增量', explain: '借钱意愿强不强' },
    { key: '社零', label: '社零增速', explain: '老百姓花不花钱' },
    { key: '出口', label: '出口总额', explain: '外贸这块卖了多少' },
    { key: '固定资产投资', label: '固投增速', explain: '工厂/基建/地产的投资热度' },
  ]


  // Pre-compute to avoid nested ternary triggering SWC parser issue
  const trendContent = !macro ? null : macro.indicators.length === 0 ? null : (
    <>
      <div className="space-y-3">
        {macro.indicators.map((ind) => (
          <div key={ind.name} className="flex items-center justify-between px-4 py-2 bg-surface-alt rounded-lg">
            <span className="text-sm font-medium text-text-primary">{ind.name}</span>
            <span className="text-sm text-text-secondary">{ind.current != null ? `${ind.current}${macroUnits[ind.name] ?? ''}` : '—'}</span>
            <span className={ind.direction === 'up' ? 'text-success' : ind.direction === 'down' ? 'text-danger' : 'text-text-muted'}>
              {ind.direction === 'up' ? '↑' : ind.direction === 'down' ? '↓' : '—'}
            </span>
            <span className="text-xs text-text-muted">{ind.source}</span>
          </div>
        ))}
      </div>
      <p className="text-xs text-text-muted mt-4">趋势图表需要更多历史数据点，功能开发中。</p>
    </>
  )

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
                别被噪音带着跑。看清市场，再出手。
              </h1>
              <p className="text-text-secondary text-[16px] mt-1 max-w-2xl leading-relaxed">
                剥离情绪与传闻，用四周期嵌套与核心宏观指标定位当前市场的真实坐标。
                不预测明天，只看清当下。
              </p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <div className="flex items-start gap-4 mb-6">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500/20 text-mango-600 text-base font-bold">
              2
            </span>
            <h2 className="text-[28px] leading-[1.15] font-bold text-text-primary tracking-title">宏观数据快照</h2>
          </div>

          {loading ? (
            <div className="text-center py-12 text-text-muted text-sm">加载中...</div>
          ) : (
            <div className="rounded-xl border border-border bg-surface overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border-light">
                      <th className="text-left px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">指标</th>
                      <th className="text-right px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">当前值</th>
                      <th className="text-center px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">趋势</th>
                      <th className="text-right px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">5年分位</th>
                      <th className="text-left px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">通俗解释</th>
                    </tr>
                  </thead>
                  <tbody>
                    {macroRows.map(({ key, label, explain }) => {
                      const ind = find(key)
                      const isAvailable = ind?.available !== false
                      return (
                        <tr key={key} className="border-t border-border-light">
                          <td className="px-5 py-3 text-sm font-medium text-text-primary">{label}</td>
                          <td className="px-5 py-3 text-right text-sm text-text-primary font-mono">
                            {!isAvailable ? (<span className="text-text-muted">数据暂不可用</span>) : ind ? `${ind.current}${macroUnits[ind.name] ?? ''}` : '暂无'}
                          </td>
                          <td className="px-5 py-3 text-center text-sm">
                            {ind ? (
                              <span className={
                                ind.direction === 'up' ? 'text-success font-medium' :
                                ind.direction === 'down' ? 'text-danger font-medium' :
                                'text-text-muted'
                              }>
                                {ind.direction === 'up' ? '↑' : ind.direction === 'down' ? '↓' : '—'}
                              </span>
                            ) : (
                              <span className="text-text-muted">—</span>
                            )}
                          </td>
                          <td className="px-5 py-3 text-right text-sm text-text-secondary">
                            {ind ? `${ind.percentile}%` : '—'}
                          </td>
                          <td className="px-5 py-3 text-sm text-text-secondary">{explain}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
                <div className="px-5 py-3 text-xs text-text-muted border-t border-border-light">
                  数据来源：{macro?.indicators[0]?.source || '国家统计局/央行/海关总署'} · 更新：{macro?.updated_at || '—'}
                </div>
              </div>
            </div>
          )}
        </section>

        <section className="mb-10">
          <div className="flex items-start gap-4 mb-6">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500/20 text-mango-600 text-base font-bold">
              3
            </span>
            <h2 className="text-[28px] leading-[1.15] font-bold text-text-primary tracking-title">趋势验证</h2>
          </div>
            <div className="rounded-xl border border-border bg-surface p-8">
              {loading ? (
                <div className="text-center py-4 text-text-muted text-sm">加载中...</div>
              ) : trendContent ? (
                trendContent
              ) : (
                <div className="text-center py-4 text-text-muted text-sm">暂无数据</div>
              )}
            </div>
        </section>

        <section className="mb-10">
          <div className="flex items-start gap-4 mb-6">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500/20 text-mango-600 text-base font-bold">
              4
            </span>
            <h2 className="text-[28px] leading-[1.15] font-bold text-text-primary tracking-title">四周期定位</h2>
          </div>

          <div className="overflow-x-auto rounded-xl border border-border bg-surface">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-light">
                  <th className="text-left px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label"></th>
                  {cycles.map(c => (
                    <th key={c.name} className="text-left px-5 py-3">
                      <div className="text-sm font-semibold text-text-primary">{c.name}</div>
                      <div className="text-xs text-text-muted font-normal">{c.period}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-border-light">
                  <td className="px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">判断指标</td>
                  {cycles.map(c => (
                    <td key={c.name} className="px-5 py-3">
                      <div className="text-xs text-text-muted">{c.indicators.join(' / ')}</div>
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-border-light">
                  <td className="px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">当前数据</td>
                  {cycles.map(c => (
                    <td key={c.name} className="px-5 py-3">
                      {c.currentData.map((d, i) => (
                        <div key={i} className="text-sm text-text-primary mb-0.5">
                          <span className="text-text-muted text-xs">{d.label} </span>
                          <span className="font-mono">{d.value}</span>
                        </div>
                      ))}
                    </td>
                  ))}
                </tr>
                <tr className="border-b border-border-light">
                  <td className="px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">历史分位</td>
                  {cycles.map(c => (
                    <td key={c.name} className="px-5 py-3">
                      {c.percentile > 0 ? (
                        <div>
                          <div className="text-sm font-semibold text-text-primary mb-1">{c.percentile}%</div>
                          <div className="w-full h-2 rounded-full bg-surface-alt overflow-hidden">
                            <div
                              className="h-full rounded-full bg-mango-500"
                              style={{ width: `${c.percentile}%` }}
                            />
                          </div>
                        </div>
                      ) : (
                        <span className="text-xs text-text-muted">—</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="px-5 py-3 text-xs text-text-muted font-medium uppercase tracking-label">历史参考</td>
                  {cycles.map(c => (
                    <td key={c.name} className="px-5 py-3">
                      <p className="text-xs text-text-secondary leading-relaxed">{c.historyNote}</p>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className="mb-10">
          <details className="rounded-xl border border-border bg-surface p-5 group">
            <summary className="cursor-pointer text-sm font-medium text-text-primary list-none flex items-center justify-between">
              每个周期是什么？
              <span className="text-xs text-text-muted group-open:hidden">展开</span>
              <span className="text-xs text-text-muted hidden group-open:inline">收起</span>
            </summary>
            <div className="mt-4 space-y-3 text-sm text-text-secondary leading-relaxed">
              <p><strong>基钦周期</strong>（3-4 年）：库存周期。货多了降价清仓，货少了涨价补库，三四年一个来回。最短也最容易被感知。</p>
              <p><strong>朱格拉周期</strong>（7-11 年）：设备周期。工厂换机器、企业更新设备，七八年来一轮。当前处于新旧动能交替期。</p>
              <p><strong>库兹涅茨周期</strong>（15-20 年）：房地产周期。一轮完整的涨跌牵动上下游几十个行业，影响一代人的资产配置。</p>
              <p><strong>康波周期</strong>（50-60 年）：技术革命周期。蒸汽机→电力→互联网→AI，每一次都是生产方式的重构。</p>
            </div>
          </details>
        </section>

        <div className="text-center text-xs text-text-muted py-4 border-t border-border-light">
          本页面仅展示历史数据，不构成任何投资建议。周期定位基于公开宏观经济指标的统计描述，不代表对未来走势的预测。
        </div>

        <div className="card border-mango-200 bg-surface-warm text-center p-8">
          <h3 className="text-h3 text-text-primary mb-2">解锁完整周期分析</h3>
          <p className="text-sm text-text-secondary mb-5 max-w-md mx-auto">
            历史市场印证 · 四周期叠加图 · 拐点预警信号——加入星球解锁全部。
          </p>
          <button className="btn-primary text-sm px-6">加入星球</button>
        </div>

      </main>
    </div>
  )
}

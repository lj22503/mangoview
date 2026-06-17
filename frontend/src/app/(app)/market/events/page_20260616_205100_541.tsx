'use client'

import { useEffect, useState } from 'react'
import { getMacroData, getNorthMoney, MacroData, NorthMoneyData } from '@/lib/api'

interface SignalEvent {
  date: string
  content: string
  industry: string
  impact: 'positive' | 'negative' | 'neutral'
  rulerScore: { name: string; score: number }[]
}

export default function EventsPage() {
  const [macro, setMacro] = useState<MacroData | null>(null)
  const [northMoney, setNorthMoney] = useState<NorthMoneyData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getMacroData(), getNorthMoney()])
      .then(([m, n]) => { setMacro(m); setNorthMoney(n) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const gateEvents: SignalEvent[] = [
    {
      date: '06-13',
      content: '全固态电池 A 样下线，锂电池产业链面临技术路线切换',
      industry: '电力设备',
      impact: 'positive',
      rulerScore: [
        { name: '不可逆性', score: 8 },
        { name: '影响半径', score: 7 },
        { name: '认知滞后', score: 5 },
      ],
    },
    {
      date: '06-10',
      content: '首套房首付降至 15%，房地产销售数据待验证',
      industry: '房地产',
      impact: 'positive',
      rulerScore: [
        { name: '不可逆性', score: 6 },
        { name: '影响半径', score: 8 },
        { name: '认知滞后', score: 4 },
      ],
    },
  ]

  const pipeEvents: SignalEvent[] = [
    {
      date: '06-16',
      content: '北向资金连续 5 日净流入，外资正在回补仓位',
      industry: '全市场',
      impact: 'positive',
      rulerScore: [
        { name: '不可逆性', score: 5 },
        { name: '影响半径', score: 9 },
        { name: '认知滞后', score: 3 },
      ],
    },
    {
      date: '06-14',
      content: '硫酸涨价 20.7%，下游化工成本压力上升',
      industry: '基础化工',
      impact: 'neutral',
      rulerScore: [
        { name: '不可逆性', score: 4 },
        { name: '影响半径', score: 7 },
        { name: '认知滞后', score: 6 },
      ],
    },
  ]

  const divergeEvents: SignalEvent[] = [
    // 本周无显著背离
  ]

  const renderStars = (score: number) => {
    const full = Math.floor(score / 2)
    return '█'.repeat(full) + '░'.repeat(5 - full)
  }

  return (
    <div className="min-h-screen bg-surface-alt">
      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* Hero */}
        <section className="mb-10">
          <div className="flex items-start gap-4 mb-5">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500 text-white text-base font-bold">
              1
            </span>
            <div>
              <h1 className="text-[32px] leading-[1.15] font-bold text-text-primary tracking-hero">
                不看新闻，看信号。
              </h1>
              <p className="text-text-secondary text-[16px] mt-1 max-w-2xl leading-relaxed">
                用三把尺子（不可逆性 / 影响半径 / 认知滞后）给事件量含金量——
                闸门看新赛道有没有开，管道看钱在往哪流，背离看有没有人看漏的机会。
              </p>
            </div>
          </div>
        </section>

        {/* 综合信号看板 */}
        <section className="mb-10">
          <div className="flex items-start gap-4 mb-6">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500/20 text-mango-600 text-base font-bold">
              2
            </span>
            <h2 className="text-[28px] leading-[1.15] font-bold text-text-primary tracking-title">综合看板</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-xl border border-border bg-surface p-5">
              <p className="text-xs text-text-muted mb-3 uppercase tracking-label">周期坐标</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-mango-500" />
                  <span className="text-sm text-text-primary">基钦周期：分位偏低</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-mango-500" />
                  <span className="text-sm text-text-primary">朱格拉：新旧动能交替</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-border" />
                  <span className="text-sm text-text-muted">库兹涅茨：地产出清中</span>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-border bg-surface p-5">
              <p className="text-xs text-text-muted mb-3 uppercase tracking-label">估值水位</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-mango-500" />
                  <span className="text-sm text-text-primary">PE 分位均值：合理偏低</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-border" />
                  <span className="text-sm text-text-muted">无显著泡沫</span>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-border bg-surface p-5">
              <p className="text-xs text-text-muted mb-3 uppercase tracking-label">边际变化</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-mango-500" />
                  <span className="text-sm text-text-primary">北向资金持续流入</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-mango-500" />
                  <span className="text-sm text-text-primary">PMI 连续 3 月扩张</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-border" />
                  <span className="text-sm text-text-muted">背离信号暂未触发</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 北向资金 */}
        <section className="mb-10">
          <h2 className="text-xl font-semibold text-text-primary mb-4">北向资金</h2>
          {loading ? (
            <div className="text-center py-8 text-text-muted text-sm">加载中...</div>
          ) : northMoney ? (
            <div className="space-y-3">
              <div className="rounded-xl border border-border bg-surface p-5 flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-muted">今日净买入</p>
                  <p className={`text-2xl font-semibold ${northMoney.net_buy >= 0 ? 'text-success' : 'text-danger'}`}>
                    {northMoney.net_buy >= 0 ? '+' : ''}{northMoney.net_buy}亿
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-text-muted">沪深300涨跌幅</p>
                  <p className={`text-2xl font-semibold font-mono ${northMoney.hs300_change >= 0 ? 'text-success' : 'text-danger'}`}>
                    {northMoney.hs300_change >= 0 ? '+' : ''}{northMoney.hs300_change}%
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl border border-border bg-surface p-4">
                  <p className="text-xs text-text-muted mb-1">买入成交额</p>
                  <p className="text-lg font-semibold text-text-primary">{northMoney.buy_amount}亿</p>
                </div>
                <div className="rounded-xl border border-border bg-surface p-4">
                  <p className="text-xs text-text-muted mb-1">卖出成交额</p>
                  <p className="text-lg font-semibold text-text-primary">{northMoney.sell_amount}亿</p>
                </div>
              </div>
              <p className="text-xs text-text-muted">数据来源：沪深港交所 · 更新：{northMoney.updated_at}</p>
            </div>
          ) : (
            <div className="text-center py-8 text-text-muted text-sm">数据加载失败</div>
          )}
        </section>

        {/* 近期信号（按类型分组） */}
        <section className="mb-10">
          <h2 className="text-xl font-semibold text-text-primary mb-4">近期信号</h2>

          {/* 闸门信号 */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <span className="w-3 h-3 rounded-full bg-success" />
              <h3 className="text-sm font-semibold text-text-primary">闸门信号 · 新赛道在开启</h3>
              <span className="text-xs text-text-muted bg-surface-alt px-2 py-0.5 rounded">{gateEvents.length}条</span>
            </div>
            {gateEvents.length > 0 ? (
              <div className="space-y-3">
                {gateEvents.map((e, i) => (
                  <div key={i} className="rounded-lg border border-border bg-surface p-4">
                    <div className="flex items-start gap-3">
                      <span className="text-xs text-text-muted shrink-0 mt-0.5">{e.date}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="text-sm text-text-primary">{e.content}</p>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-text-muted mb-2">
                          <span>影响行业：{e.industry}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          {e.rulerScore.map(r => (
                            <span key={r.name} className="text-text-muted">
                              {r.name} {renderStars(r.score)} {r.score}/10
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-lg border border-border bg-surface p-4 text-sm text-text-muted">暂无闸门信号</div>
            )}
          </div>

          {/* 管道信号 */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <span className="w-3 h-3 rounded-full bg-mango-500" />
              <h3 className="text-sm font-semibold text-text-primary">管道信号 · 钱在往这跑</h3>
              <span className="text-xs text-text-muted bg-surface-alt px-2 py-0.5 rounded">{pipeEvents.length}条</span>
            </div>
            {pipeEvents.length > 0 ? (
              <div className="space-y-3">
                {pipeEvents.map((e, i) => (
                  <div key={i} className="rounded-lg border border-border bg-surface p-4">
                    <div className="flex items-start gap-3">
                      <span className="text-xs text-text-muted shrink-0 mt-0.5">{e.date}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-text-primary mb-1">{e.content}</p>
                        <div className="flex items-center gap-3 text-xs text-text-muted mb-2">
                          <span>影响行业：{e.industry}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          {e.rulerScore.map(r => (
                            <span key={r.name} className="text-text-muted">
                              {r.name} {renderStars(r.score)} {r.score}/10
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-lg border border-border bg-surface p-4 text-sm text-text-muted">暂无管道信号</div>
            )}
          </div>

          {/* 背离信号 */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <span className="w-3 h-3 rounded-full bg-danger" />
              <h3 className="text-sm font-semibold text-text-primary">背离信号 · 有人看漏了</h3>
              <span className="text-xs text-text-muted bg-surface-alt px-2 py-0.5 rounded">{divergeEvents.length}条</span>
            </div>
            {divergeEvents.length > 0 ? (
              <div className="space-y-3">
                {divergeEvents.map((e, i) => (
                  <div key={i} className="rounded-lg border border-border bg-surface p-4">
                    <div className="flex items-start gap-3">
                      <span className="text-xs text-text-muted shrink-0 mt-0.5">{e.date}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-text-primary mb-1">{e.content}</p>
                        <div className="flex items-center gap-3 text-xs text-text-muted mb-2">
                          <span>影响行业：{e.industry}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs">
                          {e.rulerScore.map(r => (
                            <span key={r.name} className="text-text-muted">
                              {r.name} {renderStars(r.score)} {r.score}/10
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-lg border border-border bg-surface p-4 text-sm text-text-muted">本周无显著背离信号。两个指标给的信号不一致时，往往藏着预期差。</div>
            )}
          </div>
        </section>

        {/* 三把尺子说明（可展开） */}
        <section className="mb-10">
          <details className="rounded-xl border border-border bg-surface p-5 group">
            <summary className="cursor-pointer text-sm font-medium text-text-primary list-none flex items-center justify-between">
              什么是闸门 / 管道 / 背离？
              <span className="text-xs text-text-muted group-open:hidden">展开</span>
              <span className="text-xs text-text-muted hidden group-open:inline">收起</span>
            </summary>
            <div className="mt-4 space-y-3 text-sm text-text-secondary leading-relaxed">
              <p><strong>闸门信号</strong>：新赛道打开的瞬间。政策变动、技术突破、新产品开售，拉开了新的竞争格局。不是"今天涨了"，是"游戏规则变了"。尺子是<em>不可逆性</em>——这个变化能退回去吗？</p>
              <p><strong>管道信号</strong>：钱正在流动的方向。北向资金连续买入、成本端价格异动、成交量异常放大——钱不会说谎，它会告诉你市场在往哪走。尺子是<em>影响半径</em>——这个变化会波及多少行业？</p>
              <p><strong>背离信号</strong>：两个指标给的信号不一样。指数创新高但北向资金在跑，库存天量但运价在涨——不一致的地方往往藏着预期差。尺子是<em>认知滞后</em>——市场多久才会发现这个矛盾？</p>
            </div>
          </details>
        </section>

        {/* 合规声明 */}
        <div className="text-center text-xs text-text-muted py-4 border-t border-border-light">
          本页面仅展示公开市场事件与资金流向数据，不构成任何投资建议。三把尺子评分为框架方法论输出，不代表事件最终影响判断。
        </div>

        {/* 付费 */}
        <div className="card border-mango-200 bg-surface-warm text-center p-8">
          <h3 className="text-h3 text-text-primary mb-2">解锁完整事件研判</h3>
          <p className="text-sm text-text-secondary mb-5 max-w-md mx-auto">
            实时资金流预警 · 机构持仓动向 · 事件研判引擎——加入星球解锁全部。
          </p>
          <button className="btn-primary text-sm px-6">加入星球</button>
        </div>

      </main>
    </div>
  )
}

'use client'

import { useState } from 'react'
import { postPortfolioGenerate, PortfolioData } from '@/lib/api'

export default function PortfolioPage() {
  const [risk, setRisk] = useState<'conservative' | 'balanced' | 'aggressive'>('balanced')
  const [timeHorizon, setTimeHorizon] = useState('3-5 年')
  const [amount, setAmount] = useState('1000000')
  const [industries, setIndustries] = useState<string[]>([])
  const [result, setResult] = useState<PortfolioData | null>(null)
  const [loading, setLoading] = useState(false)

  const industryOptions = ['消费', '科技', '医药', '金融', '新能源', '房地产', '军工', '白酒']

  function toggleIndustry(ind: string) {
    setIndustries(prev =>
      prev.includes(ind) ? prev.filter(i => i !== ind) : [...prev, ind]
    )
  }

  async function handleGenerate() {
    setLoading(true)
    try {
      const data = await postPortfolioGenerate({
        risk_profile: risk,
        time_horizon: timeHorizon,
        investable_amount: parseFloat(amount),
        familiar_industries: industries
      })
      setResult(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface-alt">
      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* ===== Header ===== */}
        <section className="mb-10">
          <div className="flex items-start gap-4 mb-5">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500 text-white text-base font-bold">
              3
            </span>
            <div>
              <h1 className="text-[32px] leading-[1.15] font-bold text-text-primary tracking-hero">钱该放在哪？</h1>
              <p className="text-text-secondary text-[16px] mt-1 max-w-2xl leading-relaxed">
                知道周期在哪、行业如何之后，最后一步——决定配置。输入画像，引擎推算。
              </p>
            </div>
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          {/* 画像输入 */}
          <div className="rounded-xl border border-border bg-surface p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-6">输入投资画像</h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-3">风险偏好</label>
                <div className="flex gap-3">
                  {(['conservative', 'balanced', 'aggressive'] as const).map(r => (
                    <button
                      key={r}
                      onClick={() => setRisk(r)}
                      className={`px-4 py-2 rounded-lg font-medium transition-all ${
                        risk === r
                          ? 'bg-mango-500 text-white'
                          : 'border border-border text-text-secondary hover:border-mango-400'
                      }`}
                    >
                      {r === 'conservative' ? '保守' : r === 'balanced' ? '平衡' : '积极'}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-3">投资期限</label>
                <div className="flex gap-3">
                  {['1-3 年', '3-5 年', '5 年以上'].map(t => (
                    <button
                      key={t}
                      onClick={() => setTimeHorizon(t)}
                      className={`px-4 py-2 rounded-lg font-medium transition-all ${
                        timeHorizon === t
                          ? 'bg-mango-500 text-white'
                          : 'border border-border text-text-secondary hover:border-mango-400'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">可投资金（元）</label>
                <input
                  type="number"
                  value={amount}
                  onChange={e => setAmount(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-border bg-surface-alt text-text-primary focus:border-mango-400 focus:ring-2 focus:ring-mango-500/15 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-3">熟悉行业</label>
                <div className="flex flex-wrap gap-2">
                  {industryOptions.map(ind => (
                    <button
                      key={ind}
                      onClick={() => toggleIndustry(ind)}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                        industries.includes(ind)
                          ? 'bg-mango-500 text-white'
                          : 'border border-border text-text-secondary hover:border-mango-400'
                      }`}
                    >
                      {ind}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleGenerate}
                disabled={loading}
                className="w-full px-4 py-3 bg-mango-500 text-white rounded-lg font-medium hover:bg-mango-600 transition-all disabled:opacity-50"
              >
                {loading ? '推算中...' : '启动引擎推演'}
              </button>
            </div>
          </div>

          {/* 结果 */}
          <div className="rounded-xl border border-border bg-surface p-6">
            <h2 className="text-xl font-semibold text-text-primary mb-6">引擎推演</h2>

            {result ? (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-mango-600 mb-3">战略配置</h3>
                  <p className="text-sm text-text-secondary mb-4">{result.strategy.logic}</p>
                  <div className="space-y-3">
                    {Object.entries(result.strategy.allocation).map(([key, val]) => (
                      <div key={key} className="flex items-center justify-between p-3 bg-surface-alt rounded-lg">
                        <span className="text-sm font-medium text-text-primary">
                          {key === 'equity' ? '股票' : key === 'bond' ? '债券' : key === 'gold' ? '黄金' : '现金'}
                        </span>
                        <span className={`text-lg font-bold font-mono ${val.locked ? 'text-text-muted' : 'text-mango-600'}`}>
                          {val.display}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-mango-600 mb-3">战术配置</h3>
                  <p className="text-sm text-text-secondary">{result.tactics.logic}</p>
                  <div className="mt-3 p-4 bg-surface-alt rounded-lg text-center">
                    <span className="text-sm text-text-muted">具体标的 → 加入星球解锁</span>
                  </div>
                </div>

                {result.requires_subscription && (
                  <div className="p-4 bg-surface-warm rounded-lg text-center">
                    <p className="text-mango-600 font-medium">加入知识星球，解锁个性化配置方案</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center">
                <div className="text-center text-text-muted">
                  <p className="text-sm">输入参数，点击「启动引擎推演」</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

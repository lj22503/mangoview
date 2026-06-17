'use client'

import { useState } from 'react'
import { postAnalysisCycleLocator, EngineCycleResponse } from '@/lib/api'

interface Tool {
  id: string
  name: string
  hook: string
  analogy: string
  output: string
  status: 'free' | 'locked'
}

type Category = {
  name: string
  color: string
  tools: Tool[]
}

const categories: Category[] = [
  {
    name: '市场诊断',
    color: '#059669',
    tools: [
      {
        id: 'cycle-locator',
        name: '周期定位器',
        hook: '现在是什么周期？',
        analogy: '就像听音乐，先搞清楚现在播到哪首歌了',
        output: '四周期嵌套位置 + 历史对照 + 配置建议',
        status: 'free'
      }
    ]
  },
  {
    name: '估值分析',
    color: '#3b82f6',
    tools: [
      {
        id: 'value-analyzer',
        name: '价值评估器',
        hook: '这个东西贵不贵？',
        analogy: '用便宜的价格买值钱的东西——格雷厄姆的安全边际',
        output: '内在价值估算 + 安全边际判断',
        status: 'free'
      },
      {
        id: 'moat-evaluator',
        name: '护城河评估',
        hook: '它凭什么能一直赚？',
        analogy: '巴菲特说要有护城河——别人抢不走的竞争优势',
        output: '护城河评级 + 竞争对手对比',
        status: 'locked'
      }
    ]
  },
  {
    name: '配置方案',
    color: '#f59e0b',
    tools: [
      {
        id: 'asset-allocator',
        name: '资产配置器',
        hook: '钱要怎么分配？',
        analogy: '不把鸡蛋放一个篮子，还要知道每个篮子放几个',
        output: '股/债/金/现金配置比例 + 再平衡建议',
        status: 'free'
      }
    ]
  },
  {
    name: '决策辅助',
    color: '#64748b',
    tools: [
      {
        id: 'decision-checklist',
        name: '决策清单',
        hook: '下单前再过一遍？',
        analogy: '飞行员起飞前检查清单，防止低级错误',
        output: '决策检查项 + 风险提示',
        status: 'free'
      },
      {
        id: 'bias-detector',
        name: '偏差检测',
        hook: '你可能正在过度自信',
        analogy: '人脑有系统性的思维错误，帮你照镜子',
        output: '偏见类型识别 + 纠正建议',
        status: 'locked'
      }
    ]
  },
  {
    name: '大师理念',
    color: '#7c3aed',
    tools: [
      {
        id: 'china-masters',
        name: '中国大师思想库',
        hook: '李录 / 邱国鹭 / 段永平怎么想的？',
        analogy: '站在巨人的肩膀上——几十年经验浓缩',
        output: '投资逻辑 + 应用场景',
        status: 'locked'
      }
    ]
  },
  {
    name: '事件研判',
    color: '#db2777',
    tools: [
      {
        id: 'event-analyzer',
        name: '范蠡商情',
        hook: '这个消息怎么看？',
        analogy: '范蠡商情四步心法——采集 / 选择 / 判定 / 分析',
        output: '事件评级 + 投资信号',
        status: 'locked'
      }
    ]
  }
]

export default function ToolsPage() {
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null)
  const [modalTab, setModalTab] = useState<'intro' | 'use'>('intro')

  const [pmi, setPmi] = useState('50.8')
  const [ppi, setPpi] = useState('-2.1')
  const [fixedAsset, setFixedAsset] = useState('4.0')
  const [newStart, setNewStart] = useState('-10.5')
  const [result, setResult] = useState<EngineCycleResponse | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleCycleLocator() {
    setLoading(true)
    try {
      const data = await postAnalysisCycleLocator({
        indicators: {
          pmi: parseFloat(pmi),
          ppi: parseFloat(ppi),
          fixed_asset_investment: parseFloat(fixedAsset),
          new_start_area: parseFloat(newStart)
        }
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
          <h1 className="text-[32px] leading-[1.15] font-bold text-text-primary tracking-hero mb-2">工具集</h1>
          <p className="text-text-secondary text-[16px]">选一个工具，回答心里那个投资问题</p>
        </section>

        <div className="space-y-8">
          {categories.map(cat => (
            <div key={cat.name}>
              <h2 className="text-lg font-semibold mb-4" style={{ color: cat.color }}>
                {cat.name}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {cat.tools.map(tool => (
                  <div
                    key={tool.id}
                    className="rounded-xl border border-border bg-surface p-6 hover:border-mango-400 transition-all cursor-pointer group"
                    onClick={() => setSelectedTool(tool)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                        tool.status === 'free'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-surface-warm text-mango-600'
                      }`}>
                        {tool.status === 'free' ? '免费' : '星球'}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">{tool.name}</h3>
                    <p className="text-sm text-mango-600 font-medium mb-2">「{tool.hook}」</p>
                    <p className="text-xs text-text-secondary mb-3">{tool.analogy}</p>
                    <div className="text-xs text-text-muted">
                      <span className="text-text-secondary">输出：</span>{tool.output}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Tool Modal */}
      {selectedTool && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-2xl max-w-xl w-full shadow-2xl overflow-hidden">
            <div className="bg-surface-warm p-6 border-b border-border">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-text-primary">{selectedTool.name}</h3>
                  <p className="text-sm text-mango-600 mt-0.5">「{selectedTool.hook}」</p>
                </div>
                <button
                  onClick={() => { setSelectedTool(null); setResult(null); setModalTab('intro') }}
                  className="text-text-muted hover:text-text-primary text-2xl w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-alt"
                >&times;</button>
              </div>
            </div>

            {selectedTool.status === 'free' && (
              <div className="flex border-b border-border">
                <button
                  onClick={() => setModalTab('intro')}
                  className={`flex-1 py-3 text-sm font-medium transition-colors ${
                    modalTab === 'intro'
                      ? 'text-mango-600 border-b-2 border-mango-500'
                      : 'text-text-muted'
                  }`}
                >
                  工具介绍
                </button>
                <button
                  onClick={() => setModalTab('use')}
                  className={`flex-1 py-3 text-sm font-medium transition-colors ${
                    modalTab === 'use'
                      ? 'text-mango-600 border-b-2 border-mango-500'
                      : 'text-text-muted'
                  }`}
                >
                  立即使用
                </button>
              </div>
            )}

            <div className="p-6 max-h-96 overflow-y-auto">
              {selectedTool.status === 'locked' ? (
                <div className="text-center py-8">
                  <h4 className="text-lg font-semibold text-text-primary mb-2">这个工具在星球里</h4>
                  <p className="text-sm text-text-secondary mb-6">
                    加入知识星球，解锁完整工具功能
                  </p>
                  <button className="btn-primary text-sm px-6">
                    加入星球解锁
                  </button>
                </div>
              ) : modalTab === 'intro' ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-text-muted mb-1">通俗类比</h4>
                    <p className="text-sm text-text-primary">{selectedTool.analogy}</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-text-muted mb-1">能给你什么</h4>
                    <p className="text-sm text-text-primary">{selectedTool.output}</p>
                  </div>
                  <div className="pt-4 border-t border-border">
                    <button
                      onClick={() => setModalTab('use')}
                      className="btn-primary text-sm w-full"
                    >
                      开始使用
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  {selectedTool.id === 'cycle-locator' && !result && (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1">PMI（采购经理指数）</label>
                        <input type="number" value={pmi} onChange={e => setPmi(e.target.value)}
                          className="w-full px-4 py-2 rounded-lg border border-border bg-surface-alt text-text-primary focus:border-mango-400 focus:ring-2 focus:ring-mango-500/15 outline-none" placeholder="50.8" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1">PPI（生产者价格指数）同比</label>
                        <input type="number" value={ppi} onChange={e => setPpi(e.target.value)}
                          className="w-full px-4 py-2 rounded-lg border border-border bg-surface-alt text-text-primary focus:border-mango-400 focus:ring-2 focus:ring-mango-500/15 outline-none" placeholder="-2.1" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1">固定资产投资增速（%）</label>
                        <input type="number" value={fixedAsset} onChange={e => setFixedAsset(e.target.value)}
                          className="w-full px-4 py-2 rounded-lg border border-border bg-surface-alt text-text-primary focus:border-mango-400 focus:ring-2 focus:ring-mango-500/15 outline-none" placeholder="4.0" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-text-secondary mb-1">新开工面积增速（%）</label>
                        <input type="number" value={newStart} onChange={e => setNewStart(e.target.value)}
                          className="w-full px-4 py-2 rounded-lg border border-border bg-surface-alt text-text-primary focus:border-mango-400 focus:ring-2 focus:ring-mango-500/15 outline-none" placeholder="-10.5" />
                      </div>
                      <button
                        onClick={handleCycleLocator}
                        disabled={loading}
                        className="btn-primary text-sm w-full disabled:opacity-50"
                      >
                        {loading ? '分析中...' : '开始分析'}
                      </button>
                    </div>
                  )}

                  {selectedTool.id === 'cycle-locator' && result && (
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-text-muted mb-3">四周期嵌套定位</h4>
                        <div className="grid grid-cols-2 gap-3">
                          {[
                            { name: '基钦周期', value: result.cycle_position.kitchin },
                            { name: '朱格拉周期', value: result.cycle_position.juglar },
                            { name: '库兹涅茨周期', value: result.cycle_position.kuznets },
                            { name: '康波周期', value: result.cycle_position.kondratieff }
                          ].map(item => (
                            <div key={item.name} className="bg-surface-alt p-3 rounded-lg">
                              <div className="text-xs text-text-muted">{item.name}</div>
                              <div className="text-base font-semibold text-mango-600">{item.value}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-text-muted mb-3">配置建议</h4>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.entries(result.allocation_suggestion as Record<string, string>).map(([key, val]) => (
                            <div key={key} className="flex items-center justify-between p-2 bg-surface-alt rounded-lg text-sm">
                              <span className="text-text-secondary">{key}</span>
                              <span className={`font-medium ${
                                val === '优先' ? 'text-success' : val === '回避' ? 'text-danger' : 'text-text-muted'
                              }`}>{val}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <button
                        onClick={() => setResult(null)}
                        className="w-full px-4 py-2 border border-border rounded-lg text-text-secondary hover:border-mango-400"
                      >
                        重新输入
                      </button>
                    </div>
                  )}

                  {selectedTool.id !== 'cycle-locator' && (
                    <div className="text-center py-8">
                      <p className="text-sm text-text-secondary">该工具正在接入中...</p>
                      <button
                        onClick={() => setModalTab('intro')}
                        className="mt-4 px-4 py-2 border border-border rounded-lg text-text-secondary hover:border-mango-400"
                      >
                        返回介绍
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

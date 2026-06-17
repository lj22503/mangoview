import Link from 'next/link'
import { TrendingUp, BarChart3, Wallet, ChevronRight } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-surface-alt">

      {/* ===== Hero ===== */}
      <section className="py-32 md:py-40 bg-surface">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h1 className="text-[64px] leading-[1.05] font-bold text-text-primary tracking-hero">
            看盘最少的人，<br />赚得最多
          </h1>
          <p className="text-[17px] text-text-secondary mt-6 max-w-lg mx-auto leading-relaxed">
            他们不看 K 线。他们看周期在哪、行业如何、配置对不对。
          </p>
          <p className="text-[17px] text-text-secondary max-w-lg mx-auto leading-relaxed">
            这叫<span className="text-mango-600 font-semibold">三层决策框架</span>——自上而下，每一步都有依据。
          </p>
          <div className="flex items-center justify-center gap-4 mt-10">
            <Link href="/about" className="btn-primary text-base px-6 h-11">
              了解框架
              <ChevronRight className="w-4 h-4 ml-1" />
            </Link>
            <Link href="/market" className="text-sm text-text-secondary hover:text-text-primary transition-colors">
              直接试试
            </Link>
          </div>
        </div>
      </section>

      {/* ===== 三层决策框架 ===== */}
      <section className="py-24 bg-surface-alt">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2 className="text-display text-text-primary tracking-title">不看盘的人在看什么</h2>
            <p className="text-text-secondary mt-2 text-[16px]">
              三层决策，每层回答一个问题
            </p>
          </div>

          <div className="space-y-4">
            {/* 第 1 层：数据层 */}
            <div className="rounded-xl border border-border bg-surface p-7 flex gap-5 items-start group hover:border-mango-400 transition-colors">
              <span className="shrink-0 inline-flex items-center justify-center w-14 h-14 rounded-xl bg-mango-500 text-white text-lg font-bold">
                1
              </span>
              <div className="flex-1 min-w-0">
                <h3 className="text-[20px] font-semibold text-text-primary mb-1">现在是什么周期？</h3>
                <p className="text-sm text-text-secondary mb-4">宏观周期 · 行业景气 · 资金流向</p>
                <div className="flex flex-wrap gap-1.5">
                  {['PMI', 'CPI', 'GDP', 'PPI', '社融'].map(t => (
                    <span key={t} className="px-2.5 py-1 bg-surface-alt border border-border-light rounded-md text-[11px] text-text-muted font-mono">{t}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* 第 2 层：工具层 */}
            <div className="rounded-xl border border-border bg-surface p-7 flex gap-5 items-start group hover:border-mango-400 transition-colors">
              <span className="shrink-0 inline-flex items-center justify-center w-14 h-14 rounded-xl bg-mango-500/15 text-mango-600 text-lg font-bold">
                2
              </span>
              <div className="flex-1 min-w-0">
                <h3 className="text-[20px] font-semibold text-text-primary mb-1">行业机会在哪？</h3>
                <p className="text-sm text-text-secondary mb-4">周期定位 · 行业分析 · 估值评估</p>
                <div className="flex flex-wrap gap-1.5">
                  {['周期定位', '行业分析', '价值评估'].map(t => (
                    <span key={t} className="px-2.5 py-1 bg-surface-alt border border-border-light rounded-md text-[11px] text-text-muted">{t}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* 第 3 层：配置层 */}
            <div className="rounded-xl border border-border bg-surface p-7 flex gap-5 items-start group hover:border-mango-400 transition-colors">
              <span className="shrink-0 inline-flex items-center justify-center w-14 h-14 rounded-xl bg-mango-500/8 text-mango-600 text-lg font-bold">
                3
              </span>
              <div className="flex-1 min-w-0">
                <h3 className="text-[20px] font-semibold text-text-primary mb-1">钱该放在哪？</h3>
                <p className="text-sm text-text-secondary mb-4">资产配置 · 机会追踪 · 风险控制</p>
                <div className="flex flex-wrap gap-1.5">
                  {['资产配置', '决策清单', '偏差检测'].map(t => (
                    <span key={t} className="px-2.5 py-1 bg-surface-alt border border-border-light rounded-md text-[11px] text-text-muted">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 这不是天赋，是方法 ===== */}
      <section className="py-24 bg-surface">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-display text-text-primary text-center mb-3 tracking-title">这不是天赋，是方法</h2>
          <p className="text-text-secondary text-center mb-12 max-w-lg mx-auto text-[16px]">
            同样投入时间，差距不在智商，在于有没有决策框架。
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* 凭感觉 */}
            <div className="rounded-xl border border-border bg-surface-alt p-5">
              <p className="text-xs text-text-muted font-medium mb-5 uppercase tracking-label">凭感觉</p>
              <p className="text-sm text-text-secondary leading-relaxed">
                看 K 线、追热点、凭直觉操作。行情好时觉得是股神，不好时反复怀疑。
              </p>
              <div className="mt-5 pt-4 border-t border-border-light">
                <span className="text-xs text-text-muted">每天都看盘，决策没依据</span>
              </div>
            </div>

            {/* 靠消息 */}
            <div className="rounded-xl border border-border bg-surface-alt p-5">
              <p className="text-xs text-text-muted font-medium mb-5 uppercase tracking-label">靠消息</p>
              <p className="text-sm text-text-secondary leading-relaxed">
                关注几十个公众号，跟群推荐买。信息越多越焦虑，越焦虑越操作。
              </p>
              <div className="mt-5 pt-4 border-t border-border-light">
                <span className="text-xs text-text-muted">信息过载，越做越错</span>
              </div>
            </div>

            {/* 建体系 */}
            <div className="rounded-xl border border-mango-400 bg-surface-warm p-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-20 h-20 bg-mango-500/5 rounded-bl-[40px]" />
              <p className="text-xs text-mango-600 font-semibold mb-5 uppercase tracking-label">建体系</p>
              <p className="text-sm text-text-secondary leading-relaxed">
                不看盘，看框架。从周期到行业到配置，每个决策有据可查。
              </p>
              <div className="mt-5 pt-4 border-t border-mango-200">
                <span className="text-2xl font-semibold text-mango-600">63%</span>
                <span className="text-xs text-text-secondary ml-1.5">机构投资者使用体系化方法</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 开始你的三层决策 ===== */}
      <section className="py-24 bg-surface-alt">
        <div className="max-w-5xl mx-auto px-6">
          <h2 className="text-display text-text-primary text-center mb-12 tracking-title">用框架，不用盯盘</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/market" className="card group hover:border-mango-400 transition-colors p-6">
              <BarChart3 className="w-6 h-6 text-mango-500 mb-4" strokeWidth={1.5} />
              <h3 className="font-semibold text-text-primary mb-1 tracking-card-title group-hover:text-mango-600 transition-colors">市场周期看版</h3>
              <p className="text-xs text-text-muted mb-5">四周期嵌套 · 行业景气 · 资金流向</p>
              <span className="text-sm font-medium text-mango-500 flex items-center gap-1">
                查看 <ChevronRight className="w-4 h-4" />
              </span>
            </Link>

            <Link href="/market/cycle" className="card group hover:border-mango-400 transition-colors p-6">
              <TrendingUp className="w-6 h-6 text-mango-500 mb-4" strokeWidth={1.5} />
              <h3 className="font-semibold text-text-primary mb-1 tracking-card-title group-hover:text-mango-600 transition-colors">周期定位器</h3>
              <p className="text-xs text-text-muted mb-5">四周期嵌套分析，判断当前位置</p>
              <span className="text-sm font-medium text-mango-500 flex items-center gap-1">
                使用 <ChevronRight className="w-4 h-4" />
              </span>
            </Link>

            <Link href="/portfolio" className="card group hover:border-mango-400 transition-colors p-6">
              <Wallet className="w-6 h-6 text-mango-500 mb-4" strokeWidth={1.5} />
              <h3 className="font-semibold text-text-primary mb-1 tracking-card-title group-hover:text-mango-600 transition-colors">资产配置器</h3>
              <p className="text-xs text-text-muted mb-5">一键生成专属配置方案</p>
              <span className="text-sm font-medium text-mango-500 flex items-center gap-1">
                使用 <ChevronRight className="w-4 h-4" />
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* ===== Footer ===== */}
      <footer className="border-t border-border py-12">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <p className="text-[18px] font-semibold text-text-primary mb-4">
            少看盘，多看看三层。
          </p>
          <div className="bg-mango-100 rounded-lg p-4 mb-6 max-w-xl mx-auto">
            <p className="text-xs text-text-secondary leading-relaxed">
              本平台提供投资框架与数据参考，不构成任何投资建议。市场有风险，投资需谨慎。
            </p>
          </div>
          <p className="text-xs text-text-muted">© 2026 Mangfolio</p>
        </div>
      </footer>
    </div>
  )
}

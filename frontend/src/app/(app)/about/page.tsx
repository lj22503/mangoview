import { ChevronRight } from 'lucide-react'
import Link from 'next/link'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-surface-alt">
      <main className="max-w-3xl mx-auto px-6 py-12 space-y-12">

        {/* ===== 叙事承接 Hero ===== */}
        <section>
          <h1 className="text-[36px] leading-[1.15] font-bold text-text-primary tracking-hero">
            为什么看盘最少的人，赚得最多
          </h1>
          <p className="text-[16px] text-text-secondary mt-4 leading-relaxed">
            他们不是在猜——是在<span className="text-mango-600 font-semibold">定位</span>。
            定位周期在哪、行业如何、配置对不对。三件事做完，不需要每分钟盯着涨跌。
          </p>
        </section>

        {/* ===== 免责声明（提前，但叙事化包装） ===== */}
        <div className="bg-surface-warm rounded-xl p-5 border border-mango-200">
          <p className="text-sm text-text-secondary leading-relaxed">
            本平台提供投资框架与数据参考，不构成任何投资建议。市场有风险，投资需谨慎。
          </p>
        </div>

        {/* ===== 框架说明 ===== */}
        <section>
          <h2 className="text-[24px] font-semibold text-text-primary mb-5 tracking-title">三层决策框架</h2>
          <div className="space-y-3">
            <div className="rounded-xl border border-border bg-surface p-5">
              <span className="text-xs text-mango-600 font-semibold uppercase tracking-label">第一层 · 数据</span>
              <h3 className="text-[17px] font-semibold text-text-primary mt-1 mb-1">现在是什么周期？</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                基钦周期（40月）→ 朱格拉周期（8-10年）→ 库兹涅茨周期（15-20年）→ 康波周期（50年）。
                四周期嵌套定位，告诉你市场大概在什么位置。不求精确预测，只求不被方向搞反。
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-5">
              <span className="text-xs text-mango-600 font-semibold uppercase tracking-label">第二层 · 工具</span>
              <h3 className="text-[17px] font-semibold text-text-primary mt-1 mb-1">行业机会在哪？</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                格雷厄姆的安全边际、巴菲特的护城河、达利欧的全天候——经典投资框架被外化为可复用的工具。
                不是让你背理论，是让理论帮你做判断。
              </p>
            </div>

            <div className="rounded-xl border border-border bg-surface p-5">
              <span className="text-xs text-mango-600 font-semibold uppercase tracking-label">第三层 · 配置</span>
              <h3 className="text-[17px] font-semibold text-text-primary mt-1 mb-1">钱该放在哪？</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                基于你的风险偏好、资金规模、投资期限，引擎综合前两层数据输出配置方案。
                不是告诉你买什么——是告诉你钱怎么分。
              </p>
            </div>
          </div>
        </section>

        {/* ===== 数据源 ===== */}
        <section>
          <h2 className="text-[24px] font-semibold text-text-primary mb-4 tracking-title">数据来源</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              { name: '国家统计局', desc: 'GDP / CPI / PMI / PPI' },
              { name: '东方财富', desc: '大盘指数 / 行业板块 / 北向资金' },
              { name: '新浪财经', desc: '实时行情数据' },
              { name: '港交所披露易', desc: '南北向资金数据' },
            ].map(src => (
              <div key={src.name} className="rounded-lg border border-border bg-surface p-3.5">
                <p className="text-sm font-medium text-text-primary">{src.name}</p>
                <p className="text-xs text-text-muted mt-0.5">{src.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ===== 产品边界 ===== */}
        <section>
          <h2 className="text-[24px] font-semibold text-text-primary mb-4 tracking-title">产品边界</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border border-border bg-surface p-5">
              <p className="text-sm font-semibold text-mango-600 mb-3">MangoView 是</p>
              <ul className="text-sm text-text-secondary space-y-2">
                <li>数据 + 工具 + 框架的 SaaS 平台</li>
                <li>帮你建立自己的投资体系</li>
                <li>提供分析方法和决策辅助</li>
              </ul>
            </div>
            <div className="rounded-xl border border-border bg-surface p-5">
              <p className="text-sm font-semibold text-text-secondary mb-3">MangoView 不是</p>
              <ul className="text-sm text-text-secondary space-y-2">
                <li>直接提供买卖建议的投顾</li>
                <li>单纯的数据堆砌</li>
                <li>保证收益的投资产品</li>
              </ul>
            </div>
          </div>
        </section>

        {/* ===== 知识星球 + CTA ===== */}
        <section className="rounded-xl bg-surface-warm border border-mango-200 p-6">
          <h2 className="text-[20px] font-semibold text-text-primary mb-3">
            加入知识星球，解锁全部功能
          </h2>
          <ul className="text-sm text-text-secondary space-y-1.5 mb-5">
            <li>解锁全部高级工具（降秩 / 回测 / 事件研判 / 偏差检测）</li>
            <li>解锁个性化配置方案（比例 / 标的 / 分批计划）</li>
            <li>解锁完整报告 + 实时推送 + 历史归档</li>
            <li>AI 分析额度（100 次 / 月）</li>
          </ul>
          <Link
            href="/market"
            className="btn-primary inline-flex items-center gap-1 text-sm px-5 h-10"
          >
            开始使用
            <ChevronRight className="w-4 h-4" />
          </Link>
        </section>
      </main>
    </div>
  )
}

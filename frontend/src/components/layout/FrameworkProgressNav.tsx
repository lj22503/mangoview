'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { RefreshCw, Building2, Zap, ChevronRight, Check } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

/**
 * 三层六步框架的步骤定义
 *
 * 天时层（宏观）：① 周期定位 → ② 情景分析
 * 地利层（中观）：③ 行业格局 → ④ 事件驱动
 * 人和层（微观）：⑤ 机构行为 → ⑥ 大师智慧
 *
 * 前端页面映射：
 *   /market/cycle    → 天时层（合并①②：周期定位 + 情景分析）
 *   /market/industry → 地利层（合并③④：行业大图 + 事件驱动）
 *   /market/events   → 人和层（合并⑤⑥：信号扫描 + 大师视角）
 */

interface StepDefinition {
  id: string
  route: string
  layerName: string           // 层名：天时 / 地利 / 人和
  layerLabel: string           // 层标签短称
  subSteps: string[]           // 该层包含的六步中子步骤
  icon: LucideIcon
  /** 这一步看什么 — 一句话定位 */
  whatYouSee: string
  /** 为什么先看这一步 — 框架逻辑 */
  whyFirst: string
  /** 这一步怎么看 — 分析方法 */
  howToRead: string
  /** 和上一步的关系 — 递进逻辑（第一步为空） */
  relationToPrevious: string
  /** 看完了意味着什么 — 完成后的状态 */
  completionInsight: string
}

const FRAMEWORK_STEPS: StepDefinition[] = [
  {
    id: 'tianshi',
    route: '/market/cycle',
    layerName: '天时',
    layerLabel: '宏观层',
    subSteps: ['周期定位', '情景分析'],
    icon: RefreshCw,
    whatYouSee: '判断宏观经济处于什么季节',
    whyFirst:
      '自上而下的起点。就像出门先看天气——大环境决定了大类资产的胜率。' +
      '经济在扩张还是收缩、流动性是松是紧，决定了后面所有行业和个股的贝塔底色。',
    howToRead:
      '不用纠结精确预测。看三件事就够了：PMI 在 50 以上还是以下（扩张/收缩）、' +
      'PPI 在往上还是往下（企业利润方向）、政策在加码还是收紧（流动性方向）。' +
      '四周期嵌套帮你从不同时间尺度交叉验证，避免被单一指标误导。',
    relationToPrevious: '',
    completionInsight:
      '确认了宏观季节后，就知道该配进攻型还是防御型资产。' +
      '下一步进入地利层——在正确的季节里，找对的地块。',
  },
  {
    id: 'dili',
    route: '/market/industry',
    layerName: '地利',
    layerLabel: '中观层',
    subSteps: ['行业格局', '事件驱动'],
    icon: Building2,
    whatYouSee: '锁定资金正在涌入的行业和赛道',
    whyFirst:
      '确定了季节，下一步是选赛道。同样的宏观环境，不同行业的表现天差地别。' +
      '天时告诉你"现在是春天适合播种"，地利告诉你"今年种小麦好还是种玉米好"。',
    howToRead:
      '四象限矩阵帮你一眼定位：左下角（低估值+高增速）是性价比最高的区域，' +
      '右上角（高估值+高增速）需要判断增速能否持续，左上角和右下角需要警惕。' +
      'PE 分位看估值水位，净利润增速看景气方向，渗透率和 CR3 看行业格局。',
    relationToPrevious:
      '天时层告诉你宏观在复苏中期 → 历史上这个阶段消费和制造表现最好 → ' +
      '地利层帮你验证：这些行业的 PE 分位和增速是否确实匹配这个判断。',
    completionInsight:
      '锁定了 2-3 个目标行业后，还需要验证"现在是不是入场的时机"。' +
      '下一步进入人和层——看资金和信号是否在配合。',
  },
  {
    id: 'renhe',
    route: '/market/events',
    layerName: '人和',
    layerLabel: '微观层',
    subSteps: ['机构行为', '大师智慧'],
    icon: Zap,
    whatYouSee: '验证市场信号与资金是否在配合你的判断',
    whyFirst:
      '天时和地利给你方向，人和给你时机。行业再好，如果北向资金在撤退、' +
      '没有任何催化剂事件，你的买入可能需要等更久。人和层是"最后一公里"——' +
      '帮你找到出手的时机，也用大师的智慧帮你校准心态。',
    howToRead:
      '三把尺子量信号：不可逆性（这事能退回去吗）、影响半径（波及多少行业）、' +
      '认知滞后（市场还有多久才会发现）。闸门信号看新赛道打开，管道信号看钱在流动，' +
      '背离信号找市场看漏的机会。北向资金是最诚实的镜子。',
    relationToPrevious:
      '地利层锁定了 2-3 个行业 → 人和层帮你确认：这些行业有没有催化剂事件、' +
      '北向资金是在进还是出、机构持仓在加仓还是减仓。' +
      '三把尺子给事件打分，避免"听风就是雨"。',
    completionInsight:
      '三个层次走完，你完成了从宏观到微观的系统化分析。' +
      '现在可以回到配置中心，根据分析结论调整你的资产配置了。',
  },
]

export default function FrameworkProgressNav() {
  const pathname = usePathname()

  // 确定当前是哪个步骤
  const currentStepIndex = FRAMEWORK_STEPS.findIndex(
    (step) => pathname === step.route || pathname.startsWith(step.route + '/')
  )
  const currentStep = currentStepIndex >= 0 ? FRAMEWORK_STEPS[currentStepIndex] : null

  // 如果不在框架页面的三个路由中，不渲染
  if (!currentStep) return null

  return (
    <div className="bg-surface border-b border-border">
      <div className="max-w-5xl mx-auto px-6">
        {/* ===== 上层：三步进度条 ===== */}
        <div className="flex items-center pt-5 pb-3">
          {FRAMEWORK_STEPS.map((step, idx) => {
            const isCurrent = idx === currentStepIndex
            const isCompleted = idx < currentStepIndex
            const isUpcoming = idx > currentStepIndex
            const Icon = step.icon

            return (
              <div key={step.id} className="flex items-center flex-1 last:flex-none">
                {/* 步骤节点 */}
                <Link
                  href={step.route}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-lg transition-all group ${
                    isCurrent
                      ? 'bg-mango-100 text-mango-700'
                      : isCompleted
                        ? 'text-text-secondary hover:text-text-primary hover:bg-surface-alt'
                        : 'text-text-muted'
                  }`}
                >
                  {/* 状态图标 */}
                  <span
                    className={`shrink-0 inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold transition-colors ${
                      isCurrent
                        ? 'bg-mango-500 text-white'
                        : isCompleted
                          ? 'bg-success/10 text-success'
                          : 'bg-surface-alt text-text-muted border border-border'
                    }`}
                  >
                    {isCompleted ? (
                      <Check className="w-4 h-4" strokeWidth={2.5} />
                    ) : (
                      idx + 1
                    )}
                  </span>

                  {/* 文字信息 */}
                  <div className="text-left min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`text-xs font-semibold uppercase tracking-wider ${
                          isCurrent ? 'text-mango-600' : isCompleted ? 'text-text-secondary' : 'text-text-muted'
                        }`}
                      >
                        {step.layerName}
                      </span>
                      <span className="text-[10px] text-text-muted">{step.layerLabel}</span>
                    </div>
                    <div className="flex items-center gap-1 mt-0.5">
                      <Icon
                        className={`w-3.5 h-3.5 ${
                          isCurrent ? 'text-mango-500' : isCompleted ? 'text-success' : 'text-text-muted'
                        }`}
                        strokeWidth={1.5}
                      />
                      <span
                        className={`text-xs truncate ${
                          isCurrent ? 'text-text-primary font-medium' : 'text-text-muted'
                        }`}
                      >
                        {step.subSteps.join(' · ')}
                      </span>
                    </div>
                  </div>
                </Link>

                {/* 连接线 */}
                {idx < FRAMEWORK_STEPS.length - 1 && (
                  <div className="flex-1 mx-2">
                    <div
                      className={`h-0.5 rounded-full ${
                        isCompleted ? 'bg-success/40' : 'bg-border'
                      }`}
                    />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* ===== 下层：当前步骤的引导面板 ===== */}
        <div className="pb-4">
          <div className="rounded-xl bg-mango-100/50 border border-mango-200 p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* 这一页看什么 */}
              <div>
                <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                  这一步看什么
                </p>
                <p className="text-sm font-semibold text-text-primary">
                  {currentStep.whatYouSee}
                </p>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                  {currentStep.whyFirst}
                </p>
              </div>

              {/* 怎么看 */}
              <div>
                <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                  怎么看
                </p>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {currentStep.howToRead}
                </p>
              </div>

              {/* 关联与下一步 */}
              <div>
                {currentStep.relationToPrevious && (
                  <div className="mb-3">
                    <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                      与上一步的关联
                    </p>
                    <p className="text-xs text-text-secondary leading-relaxed">
                      {currentStep.relationToPrevious}
                    </p>
                  </div>
                )}

                {currentStepIndex < FRAMEWORK_STEPS.length - 1 && (
                  <div>
                    <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                      下一步
                    </p>
                    <Link
                      href={FRAMEWORK_STEPS[currentStepIndex + 1].route}
                      className="inline-flex items-center gap-1 text-xs text-mango-600 font-medium hover:text-mango-700 transition-colors"
                    >
                      {FRAMEWORK_STEPS[currentStepIndex + 1].layerName}：
                      {FRAMEWORK_STEPS[currentStepIndex + 1].whatYouSee}
                      <ChevronRight className="w-3 h-3" />
                    </Link>
                  </div>
                )}

                {currentStepIndex === FRAMEWORK_STEPS.length - 1 && (
                  <div>
                    <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                      分析完成
                    </p>
                    <p className="text-xs text-text-secondary leading-relaxed">
                      {currentStep.completionInsight}
                    </p>
                    <Link
                      href="/portfolio"
                      className="inline-flex items-center gap-1 mt-1.5 text-xs text-mango-600 font-medium hover:text-mango-700 transition-colors"
                    >
                      前往配置中心调整资产配置
                      <ChevronRight className="w-3 h-3" />
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

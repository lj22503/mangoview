'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { TrendingUp, Building2, Zap } from 'lucide-react'

/**
 * 框架子步骤标签映射
 * 天时层 → ①②周期定位+情景分析
 * 地利层 → ③④行业格局+事件驱动
 * 人和层 → ⑤⑥机构行为+大师智慧
 */
const subNavItems = [
  {
    href: '/market/cycle',
    label: '周期定位',
    stepNum: 1,
    subLabel: '天时 · 宏观层',
    subSteps: '周期定位 + 情景分析',
    icon: TrendingUp,
  },
  {
    href: '/market/industry',
    label: '行业大图',
    stepNum: 2,
    subLabel: '地利 · 中观层',
    subSteps: '行业格局 + 事件驱动',
    icon: Building2,
  },
  {
    href: '/market/events',
    label: '事件跟踪',
    stepNum: 3,
    subLabel: '人和 · 微观层',
    subSteps: '机构行为 + 大师智慧',
    icon: Zap,
  },
]

export default function MarketSubNav() {
  const pathname = usePathname()

  return (
    <div className="bg-surface border-b border-border">
      <div className="max-w-5xl mx-auto px-6">
        <div className="flex">
          {subNavItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 px-5 py-3 text-sm font-medium border-b-2 transition-colors ${
                  isActive
                    ? 'text-mango-600 border-mango-500'
                    : 'text-text-secondary border-transparent hover:text-text-primary'
                }`}
              >
                {/* 步骤编号 */}
                <span
                  className={`shrink-0 inline-flex items-center justify-center w-5 h-5 rounded text-[11px] font-bold ${
                    isActive
                      ? 'bg-mango-500 text-white'
                      : 'bg-surface-alt text-text-muted'
                  }`}
                >
                  {item.stepNum}
                </span>
                <Icon className="w-4 h-4" strokeWidth={1.5} />
                <div className="flex flex-col leading-tight">
                  <span>{item.label}</span>
                  <span className="text-[10px] text-text-muted font-normal">
                    {item.subLabel}
                  </span>
                </div>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}

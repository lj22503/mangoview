'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { TrendingUp, Building2, Zap } from 'lucide-react'

const subNavItems = [
  { href: '/market/cycle', label: '周期定位', icon: TrendingUp },
  { href: '/market/industry', label: '行业大图', icon: Building2 },
  { href: '/market/events', label: '事件跟踪', icon: Zap },
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
                className={`flex items-center gap-2 px-5 py-4 text-sm font-medium border-b-2 transition-colors ${
                  isActive
                    ? 'text-mango-600 border-mango-500'
                    : 'text-text-secondary border-transparent hover:text-text-primary'
                }`}
              >
                <Icon className="w-4 h-4" strokeWidth={1.5} />
                {item.label}
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}

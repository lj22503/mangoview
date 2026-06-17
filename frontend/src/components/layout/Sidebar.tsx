'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  CircleDollarSign,
  LayoutDashboard,
  TrendingUp,
  Building2,
  Zap,
  Target,
  FileText,
  Wrench,
  Info,
  ChevronRight,
} from 'lucide-react'

const navSections = [
  {
    label: '市场看版',
    items: [
      { href: '/market', label: '概览', icon: LayoutDashboard },
      { href: '/market/cycle', label: '周期定位', icon: TrendingUp, indent: true },
      { href: '/market/events', label: '事件跟踪', icon: Zap, indent: true },
      { href: '/market/industry', label: '行业大图', icon: Building2, indent: true },
    ],
  },
  {
    label: '',
    items: [
      { href: '/portfolio', label: '配置中心', icon: Target },
      { href: '/reports', label: '扫描报告', icon: FileText },
      { href: '/tools', label: '工具集', icon: Wrench },
    ],
  },
]

const bottomItems = [
  { href: '/about', label: '关于', icon: Info },
]

export default function Sidebar() {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/market') return pathname === '/market'
    return pathname.startsWith(href)
  }

  const isInSection = (href: string) => {
    if (href === '/market') return pathname.startsWith('/market')
    return isActive(href)
  }

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-56 bg-surface border-r border-border flex flex-col z-40">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2 px-5 h-14 shrink-0 group">
        <CircleDollarSign className="w-6 h-6 text-mango-500" strokeWidth={1.5} />
        <span className="text-lg font-semibold text-text-primary">Mangfolio</span>
      </Link>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-2 space-y-5">
        {navSections.map((section, si) => (
          <div key={si}>
            {section.label && (
              <p className="px-2 mb-1 text-[11px] font-semibold text-text-muted uppercase tracking-wider">
                {section.label}
              </p>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon
                const active = isActive(item.href)
                const inSection = isInSection(item.href)
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm transition-colors ${
                      item.indent ? 'ml-5' : ''
                    } ${
                      active
                        ? 'text-mango-600 bg-mango-100 font-medium'
                        : inSection
                          ? 'text-text-primary'
                          : 'text-text-secondary hover:text-text-primary hover:bg-surface-alt'
                    }`}
                  >
                    {Icon && <Icon className="w-4 h-4 shrink-0" strokeWidth={1.5} />}
                    <span>{item.label}</span>
                    {active && (
                      <ChevronRight className="w-3.5 h-3.5 ml-auto" strokeWidth={2} />
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Bottom */}
      <div className="px-3 py-3 border-t border-border space-y-1">
        {bottomItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2.5 px-2 py-1.5 rounded-md text-sm transition-colors ${
                active
                  ? 'text-mango-600 bg-mango-100 font-medium'
                  : 'text-text-secondary hover:text-text-primary hover:bg-surface-alt'
              }`}
            >
              {Icon && <Icon className="w-4 h-4 shrink-0" strokeWidth={1.5} />}
              <span>{item.label}</span>
            </Link>
          )
        })}
        <button className="w-full mt-2 btn-primary text-sm py-2">
          加入星球
        </button>
      </div>
    </aside>
  )
}

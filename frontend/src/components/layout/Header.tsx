'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { CircleDollarSign } from 'lucide-react'

const navItems = [
  { href: '/market', label: '市场' },
  { href: '/tools', label: '工具' },
  { href: '/portfolio', label: '配置' },
  { href: '/reports', label: '报告' },
  { href: '/about', label: '说明' },
]

export default function Header() {
  const pathname = usePathname()
  const isHome = pathname === '/'

  return (
    <header className="sticky top-0 z-50 h-14 bg-surface border-b border-border">
      <div className="max-w-6xl mx-auto h-full px-6 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <CircleDollarSign className="w-6 h-6 text-mango-500" strokeWidth={1.5} />
          <span className="text-lg font-semibold text-text-primary">
            Mangfolio
          </span>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-2 text-sm rounded-md transition-colors ${
                  isActive
                    ? 'text-mango-600 bg-mango-100 font-medium'
                    : 'text-text-secondary hover:text-text-primary hover:bg-surface-alt'
                }`}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="flex items-center gap-3">
          {isHome ? (
            <>
              <button className="text-sm text-text-secondary hover:text-text-primary transition-colors">
                登录
              </button>
              <button className="btn-primary">
                开始使用
              </button>
            </>
          ) : (
            <button className="btn-primary">
              加入星球
            </button>
          )}
        </div>
      </div>
    </header>
  )
}

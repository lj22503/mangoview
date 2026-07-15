import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MangoView - 一笔好决策，只需要看三件事',
  description: '时机对不对、公司行不行、自己有没有犯傻。Mangoview 用三层框架帮你把每一笔决策拆开来看清。',
  icons: { icon: '/favicon.svg' },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className={`${inter.className} bg-surface-alt text-text-primary min-h-screen`}>
        {children}
      </body>
    </html>
  )
}

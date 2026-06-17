import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'MangoView - 自上而下，看清每一笔投资',
  description: '基于经典框架的 SaaS 投资辅助工具',
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
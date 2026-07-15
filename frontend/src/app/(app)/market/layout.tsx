import MarketSubNav from '@/components/layout/MarketSubNav'
import FrameworkProgressNav from '@/components/layout/FrameworkProgressNav'

/**
 * /market 子路由的共享布局
 *
 * 在所有市场看版子页面（周期定位/行业大图/事件跟踪）的顶部
 * 统一渲染两层导航：
 *   1. MarketSubNav — Tab 式子页面切换，标注框架层次
 *   2. FrameworkProgressNav — 框架进度条 + 当前步骤引导面板
 *
 * 用户进入任一子页面时，自动看到自己在三层六步框架中的位置。
 */
export default function MarketLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      <MarketSubNav />
      <FrameworkProgressNav />
      {children}
    </>
  )
}

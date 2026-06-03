import Head from 'next/head'
import { MacroSnapshot } from '../components/market/macro-snapshot'
import { CyclePosition } from '../components/market/cycle-position'
import { IndustryMatrix } from '../components/market/industry-matrix'

export default function Home() {
  return (
    <>
      <Head>
        <title>MangoView - 自上而下，看清每一笔投资</title>
        <meta name="description" content="MangoView 个人投资框架面板" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-[#f8fafc]">
        {/* 顶部导航 */}
        <header className="bg-white border-b border-[#e2e8f0]">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-2xl">🥭</span>
              <span className="ml-2 text-xl font-semibold text-[#0f172a]">
                MangoView
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 bg-[#f59e0b] text-[#0f172a] rounded-lg font-medium hover:bg-[#d97706] transition-all">
                登录
              </button>
              <button className="px-4 py-2 bg-[#f59e0b] text-[#0f172a] rounded-lg font-medium hover:bg-[#d97706] transition-all">
                加入星球
              </button>
            </div>
          </div>
        </header>

        {/* 首屏 Hook */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto text-center">
              <h1 className="text-4xl md:text-5xl font-semibold text-[#0f172a] mb-6">
                3 年投资，你是在赚钱还是靠运气？
              </h1>
              <p className="text-xl text-[#64748b] mb-4">
                差别的根源不在信息，在体系。
              </p>
              <p className="text-xl text-[#64748b] mb-8">
                你属于哪一种？
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
                {/* 周期定位雷达图 */}
                <div className="bg-white rounded-xl border border-[#e2e8f0] p-6 shadow-[0_1px_3px_rgba(0,0,0,0.1)]">
                  <h3 className="text-lg font-semibold text-[#0f172a] mb-4">
                    周期定位雷达图
                  </h3>
                  <div className="text-[#94a3b8] text-sm">
                    🔒 加入星球解锁完整周期定位
                  </div>
                </div>
                
                {/* 投资 DNA */}
                <div className="bg-white rounded-xl border border-[#e2e8f0] p-6 shadow-[0_1px_3px_rgba(0,0,0,0.1)]">
                  <h3 className="text-lg font-semibold text-[#0f172a] mb-4">
                    生成你的投资 DNA
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-[#64748b] mb-2">
                        风险偏好
                      </label>
                      <div className="flex space-x-2">
                        <button className="px-3 py-1.5 border border-[#e2e8f0] rounded-lg text-sm text-[#0f172a] hover:border-[#f59e0b]">
                          保守
                        </button>
                        <button className="px-3 py-1.5 border border-[#e2e8f0] rounded-lg text-sm text-[#0f172a] hover:border-[#f59e0b]">
                          平衡
                        </button>
                        <button className="px-3 py-1.5 border border-[#e2e8f0] rounded-lg text-sm text-[#0f172a] hover:border-[#f59e0b]">
                          积极
                        </button>
                      </div>
                    </div>
                    <button className="w-full px-4 py-2 bg-[#f59e0b] text-[#0f172a] rounded-lg font-medium hover:bg-[#d97706] transition-all">
                      生成投资 DNA
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 导航 Tab */}
        <nav className="bg-white border-b border-[#e2e8f0]">
          <div className="container mx-auto px-4">
            <div className="flex space-x-8">
              <a href="/market" className="py-4 px-2 border-b-2 border-[#f59e0b] text-[#f59e0b] font-medium">
                📊 市场看版
              </a>
              <a href="/tools" className="py-4 px-2 text-[#64748b] hover:text-[#f59e0b]">
                🛠️ 工具集
              </a>
              <a href="/portfolio" className="py-4 px-2 text-[#64748b] hover:text-[#f59e0b]">
                💰 配置中心
              </a>
              <a href="/reports" className="py-4 px-2 text-[#64748b] hover:text-[#f59e0b]">
                📰 报告
              </a>
              <a href="/about" className="py-4 px-2 text-[#64748b] hover:text-[#f59e0b]">
                📖 说明
              </a>
            </div>
          </div>
        </nav>

        {/* 市场看版内容 */}
        <main className="py-8">
          <div className="container mx-auto px-4">
            <MacroSnapshot />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
              <CyclePosition />
              <IndustryMatrix />
            </div>
          </div>
        </main>

        {/* 页脚 */}
        <footer className="bg-white border-t border-[#e2e8f0] py-8">
          <div className="container mx-auto px-4 text-center">
            <p className="text-[#64748b] text-sm">
              本平台仅提供投资框架与数据参考，不构成任何投资建议。市场有风险，投资需谨慎。
            </p>
            <p className="text-[#94a3b8] text-xs mt-2">
              © 2026 MangoView. All rights reserved.
            </p>
          </div>
        </footer>
      </div>
    </>
  )
}

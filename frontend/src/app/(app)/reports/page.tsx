'use client'

import { useState, useEffect } from 'react'
import { getReports, ReportListData } from '@/lib/api'

export default function ReportsPage() {
  const [type, setType] = useState('daily')
  const [data, setData] = useState<ReportListData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getReports(type).then(setData).finally(() => setLoading(false))
  }, [type])

  return (
    <div className="min-h-screen bg-surface-alt">
      <main className="max-w-5xl mx-auto px-6 py-12">

        {/* ===== Header ===== */}
        <section className="mb-10">
          <div className="flex items-start gap-4 mb-5">
            <span className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-xl bg-mango-500 text-white text-base font-bold">
              2
            </span>
            <div>
              <h1 className="text-[32px] leading-[1.15] font-bold text-text-primary tracking-hero">扫描报告</h1>
              <p className="text-text-secondary text-[16px] mt-1 max-w-2xl leading-relaxed">
                不看盘的人看报告——每日、每周、每月，定时推送关键信号。
              </p>
            </div>
          </div>
        </section>

        {/* 类型切换 */}
        <div className="flex gap-4 mb-8">
          {[
            { key: 'daily', label: '每日', desc: '交易日 09:00 / 15:30' },
            { key: 'weekly', label: '每周', desc: '周一 10:00' },
            { key: 'monthly', label: '每月', desc: '月末' }
          ].map(t => (
            <button
              key={t.key}
              onClick={() => setType(t.key)}
              className={`px-5 py-3 rounded-xl font-medium transition-all text-left ${
                type === t.key
                  ? 'bg-mango-500 text-white'
                  : 'bg-surface border border-border text-text-secondary hover:border-mango-400'
              }`}
            >
              <div className="text-base">{t.label}</div>
              <div className="text-xs opacity-75">{t.desc}</div>
            </button>
          ))}
        </div>

        {/* 报告列表 */}
        {loading ? (
          <div className="text-center py-16 text-text-muted text-sm">加载中...</div>
        ) : (
          <div className="space-y-4">
            {data?.reports.map(report => (
              <div key={report.id} className="rounded-xl border border-border bg-surface p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="px-2 py-0.5 bg-surface-alt rounded text-xs text-text-muted">{report.type}</span>
                      <span className="text-sm text-text-muted">{report.date}</span>
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">{report.title}</h3>
                    <p className="text-sm text-text-secondary">{report.summary}</p>
                  </div>
                  {report.is_locked && (
                    <span className="shrink-0 px-3 py-1 bg-mango-500 text-white text-xs rounded-full font-medium">
                      完整版
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

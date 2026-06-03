export function CyclePosition() {
  return (
    <div className="bg-white dark:bg-[#1e293b] rounded-xl border border-[#e2e8f0] dark:border-[#334155] p-6 shadow-[0_1px_3px_rgba(0,0,0,0.1)]">
      <h2 className="text-xl font-semibold text-[#0f172a] dark:text-[#f1f5f9] mb-4">
        Tab 1: 周期定位（我们在哪？）
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-[#f8fafc] dark:bg-[#1e293b]">
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">基钦周期</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">朱格拉周期</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">库兹涅茨周期</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">康波周期</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-[#e2e8f0] dark:border-[#334155] hover:bg-[#fef3c7] dark:hover:bg-[#451a03]">
              <td className="px-4 py-3 text-sm">复苏早期</td>
              <td className="px-4 py-3 text-sm">衰退后期</td>
              <td className="px-4 py-3 text-sm">萧条期</td>
              <td className="px-4 py-3 text-sm">萧条期</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="mt-4 text-sm text-[#64748b] dark:text-[#94a3b8]">
        历史对照：2012-2013（相似度 78%）、2015-2016（相似度 65%）
      </div>
      <div className="mt-4 text-sm text-[#f59e0b]">
        🔒 历史市场印证 + 深入洞察 → [加入星球解锁]
      </div>
    </div>
  )
}

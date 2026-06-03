export function MacroSnapshot() {
  return (
    <div className="bg-white dark:bg-[#1e293b] rounded-xl border border-[#e2e8f0] dark:border-[#334155] p-6 shadow-[0_1px_3px_rgba(0,0,0,0.1)]">
      <h2 className="text-xl font-semibold text-[#0f172a] dark:text-[#f1f5f9] mb-4">
        📅 2026 年 6 月 宏观数据快照
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-[#f8fafc] dark:bg-[#1e293b]">
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">GDP</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">CPI</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">PMI</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">社融</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">PPI</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">工业利润</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">固定资产投资</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">新开工面积</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">M2</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-[#e2e8f0] dark:border-[#334155] hover:bg-[#fef3c7] dark:hover:bg-[#451a03]">
              <td className="px-4 py-3 text-sm font-mono">5.2%</td>
              <td className="px-4 py-3 text-sm font-mono">102.3</td>
              <td className="px-4 py-3 text-sm font-mono">50.8</td>
              <td className="px-4 py-3 text-sm font-mono">3.2</td>
              <td className="px-4 py-3 text-sm font-mono">-2.1%</td>
              <td className="px-4 py-3 text-sm font-mono">8.7%</td>
              <td className="px-4 py-3 text-sm font-mono">4.0%</td>
              <td className="px-4 py-3 text-sm font-mono">-10.5%</td>
              <td className="px-4 py-3 text-sm font-mono">8.7%</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

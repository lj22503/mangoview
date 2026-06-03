export function IndustryMatrix() {
  return (
    <div className="bg-white dark:bg-[#1e293b] rounded-xl border border-[#e2e8f0] dark:border-[#334155] p-6 shadow-[0_1px_3px_rgba(0,0,0,0.1)]">
      <h2 className="text-xl font-semibold text-[#0f172a] dark:text-[#f1f5f9] mb-4">
        Tab 2: 行业大图（行业在哪？）
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-[#f8fafc] dark:bg-[#1e293b]">
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">行业</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">周期阶段</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">渗透率</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">CR3</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">PE 分位</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-[#64748b]">净利润增速</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b border-[#e2e8f0] dark:border-[#334155] hover:bg-[#fef3c7] dark:hover:bg-[#451a03]">
              <td className="px-4 py-3 text-sm">消费</td>
              <td className="px-4 py-3 text-sm">复苏早期</td>
              <td className="px-4 py-3 text-sm font-mono">75%</td>
              <td className="px-4 py-3 text-sm font-mono">42%</td>
              <td className="px-4 py-3 text-sm font-mono">28.5</td>
              <td className="px-4 py-3 text-sm font-mono">12.3%</td>
            </tr>
            <tr className="border-b border-[#e2e8f0] dark:border-[#334155] hover:bg-[#fef3c7] dark:hover:bg-[#451a03]">
              <td className="px-4 py-3 text-sm">科技</td>
              <td className="px-4 py-3 text-sm">成长期</td>
              <td className="px-4 py-3 text-sm font-mono">60%</td>
              <td className="px-4 py-3 text-sm font-mono">35%</td>
              <td className="px-4 py-3 text-sm font-mono">45.2</td>
              <td className="px-4 py-3 text-sm font-mono">18.7%</td>
            </tr>
            <tr className="border-b border-[#e2e8f0] dark:border-[#334155] hover:bg-[#fef3c7] dark:hover:bg-[#451a03]">
              <td className="px-4 py-3 text-sm">医药</td>
              <td className="px-4 py-3 text-sm">成熟期</td>
              <td className="px-4 py-3 text-sm font-mono">80%</td>
              <td className="px-4 py-3 text-sm font-mono">50%</td>
              <td className="px-4 py-3 text-sm font-mono">32.1</td>
              <td className="px-4 py-3 text-sm font-mono">8.5%</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className="mt-4 text-sm text-[#f59e0b]">
        🔒 行业秩（降秩拆解） → [加入星球解锁]
      </div>
    </div>
  )
}

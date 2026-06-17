import Sidebar from '@/components/layout/Sidebar'

export default function AppLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <main className="flex-1 ml-56">
        {children}
      </main>
    </div>
  )
}

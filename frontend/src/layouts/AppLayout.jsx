import { useState } from 'react'
import Sidebar from '../components/layout/Sidebar.jsx'
import TopNav from '../components/layout/TopNav.jsx'

export default function AppLayout({ title, children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background md:flex">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 min-w-0">
        <TopNav title={title} onMenuClick={() => setSidebarOpen(true)} />
        <main className="px-container py-xl">
          <div className="max-w-[960px] mx-auto">{children}</div>
        </main>
      </div>
    </div>
  )
}

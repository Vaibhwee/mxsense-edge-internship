import { Outlet } from 'react-router-dom'
import Header from './Header.jsx'
import Sidebar from './Sidebar.jsx'

export function AppLayout() {
  return (
    <div className="h-full bg-slate-950 text-slate-100">
      <Header />
      <div className="mx-auto grid max-w-7xl grid-cols-12 gap-4 px-4 py-4">
        <aside className="col-span-12 min-w-0 md:col-span-3">
          <Sidebar />
        </aside>
        <main className="col-span-12 min-w-0 md:col-span-9">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

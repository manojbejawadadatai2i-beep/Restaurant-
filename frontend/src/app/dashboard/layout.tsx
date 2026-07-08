"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LayoutDashboard, Store, PieChart, Users, Settings, LogOut } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [roleId, setRoleId] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    } else {
      try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        setRoleId(payload.role_id);
      } catch (e) {
        console.error("Invalid token");
      }
    }
  }, [router]);

  if (!mounted) return null;

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const isCorpAdmin = roleId === "RL01";
  const isRegionOrDistrict = roleId === "RL02" || roleId === "RL03";
  const isStoreManager = roleId === "RL04";

  return (
    <div className="min-h-screen bg-slate-950 flex font-sans text-slate-200">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/50 backdrop-blur-xl border-r border-slate-800 flex flex-col p-4 z-10">
        <div className="flex items-center gap-3 px-2 mb-10 mt-4">
          <div className="w-10 h-10 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <LayoutDashboard className="text-white w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-200 to-white leading-tight">
              RestoOps
            </h1>
            <p className="text-xs text-indigo-400 font-medium">
              {roleId === 'RL01' ? 'Corporate Administrator' : 
               roleId === 'RL02' ? 'Regional Manager' :
               roleId === 'RL03' ? 'District Manager' :
               roleId === 'RL04' ? 'Store Manager' : 'Employee'}
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-2">
          {/* Everyone can see the overview dashboard (scoped to their level automatically by backend) */}
          <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20 transition-colors">
            <LayoutDashboard className="w-5 h-5" />
            <span className="font-medium">Overview</span>
          </Link>
          
          {/* Only Corporate, Regional, and District managers can view the Stores list */}
          {(isCorpAdmin || isRegionOrDistrict) && (
            <Link href="/dashboard/stores" className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-xl transition-colors">
              <Store className="w-5 h-5" />
              <span className="font-medium">Stores</span>
            </Link>
          )}

          {/* Corporate Admin gets full Reports */}
          {isCorpAdmin && (
            <Link href="/dashboard/reports" className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-xl transition-colors">
              <PieChart className="w-5 h-5" />
              <span className="font-medium">Reports</span>
            </Link>
          )}

          {/* Only Corporate Admin can manage users */}
          {isCorpAdmin && (
            <Link href="/dashboard/users" className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-xl transition-colors">
              <Users className="w-5 h-5" />
              <span className="font-medium">Team</span>
            </Link>
          )}
        </nav>

        <div className="mt-auto space-y-2 pt-8 border-t border-slate-800">
          <button className="w-full flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 rounded-xl transition-colors">
            <Settings className="w-5 h-5" />
            <span className="font-medium">Settings</span>
          </button>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Log out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {/* Abstract Background Elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2 pointer-events-none" />
        
        <div className="flex-1 overflow-auto p-8 z-10">
          {children}
        </div>
      </main>
    </div>
  );
}

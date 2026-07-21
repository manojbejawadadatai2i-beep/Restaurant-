"use client";

import { useEffect, useState } from "react";
import { Store, MapPin, Search } from "lucide-react";

import { getApiUrl } from "@/utils/config";

interface StoreData {
  store_id: string;
  store_name: string;
  district_id: string;
  total_revenue?: number;
  today_revenue?: number;
}

export default function StoresPage() {
  const [stores, setStores] = useState<StoreData[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [dateFilter, setDateFilter] = useState("all");

  useEffect(() => {
    const fetchStores = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem("token");
        const params = new URLSearchParams();
        if (dateFilter && dateFilter !== "all") {
          params.append("date", dateFilter);
        }
        const res = await fetch(`${getApiUrl("/stores")}?${params.toString()}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setStores(data);
        }
      } catch (e) {
        console.error("Failed to fetch stores", e);
      } finally {
        setLoading(false);
      }
    };
    fetchStores();
  }, [dateFilter]);

  const filtered = stores.filter(
    (s) =>
      s.store_name?.toLowerCase().includes(search.toLowerCase()) ||
      s.store_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Stores</h1>
        <p className="text-slate-400 mt-1">Manage and monitor all store locations.</p>
      </header>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row gap-4 items-center max-w-2xl">
        <div className="relative w-full sm:max-w-sm">
          <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search stores..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900/50 border border-slate-700 text-slate-200 rounded-xl py-2.5 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm placeholder:text-slate-500"
          />
        </div>
        <div className="relative w-full sm:w-auto">
          <select 
            className="w-full sm:w-48 bg-slate-900/50 border border-slate-700 text-slate-300 text-sm rounded-xl py-2.5 pl-3 pr-8 focus:ring-2 focus:ring-indigo-500 focus:outline-none appearance-none transition-all cursor-pointer hover:bg-slate-800/80"
            value={dateFilter} onChange={(e) => setDateFilter(e.target.value)}
          >
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="last7days">Last 7 Days</option>
            <option value="lastmonth">Last Month</option>
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 text-xs">▼</div>
        </div>
      </div>

      {loading ? (
        <div className="text-slate-400 text-center py-20">Loading stores...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/50 border border-slate-800 rounded-2xl">
          <Store className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No stores found in the database.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((store) => (
            <div
              key={store.store_id}
              className="relative overflow-hidden bg-slate-900/50 border border-slate-800 rounded-2xl p-5 hover:border-indigo-500/40 transition-all group cursor-pointer"
            >
              <div className="flex items-start justify-between relative z-10 transition-transform duration-300 group-hover:-translate-y-1">
                <div className="p-2 bg-indigo-500/10 rounded-xl group-hover:bg-indigo-500/20 transition-colors">
                  <Store className="w-5 h-5 text-indigo-400" />
                </div>
                <span className="text-xs text-slate-500 font-mono bg-slate-800 px-2 py-1 rounded-lg">
                  {store.store_id}
                </span>
              </div>
              
              <h3 className="text-white font-semibold mt-4 text-lg relative z-10 transition-transform duration-300 group-hover:-translate-y-1">
                {store.store_name || "Unnamed Store"}
              </h3>
              
              <div className="flex items-center gap-1.5 mt-2 text-slate-400 text-sm relative z-10 transition-transform duration-300 group-hover:-translate-y-1">
                <MapPin className="w-3.5 h-3.5" />
                <span>District: {store.district_id || "N/A"}</span>
              </div>
              
              {/* Hover overlay for Income */}
              <div className="absolute inset-0 z-20 bg-gradient-to-t from-indigo-950/90 via-slate-900/95 to-slate-900/90 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-5">
                <div className="flex justify-between items-end">
                  <div>
                    <p className="text-indigo-200 text-xs font-medium uppercase tracking-wider mb-1">Total Income</p>
                    <p className="text-white font-bold text-2xl">
                      {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(store.total_revenue || 0)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-emerald-300 text-[10px] font-medium uppercase tracking-wider mb-1">Today</p>
                    <p className="text-emerald-400 font-bold text-lg">
                      {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(store.today_revenue || 0)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

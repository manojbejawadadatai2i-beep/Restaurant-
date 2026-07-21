"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { TrendingUp, Users, DollarSign, ArrowUpRight, Clock } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

import { getApiUrl } from "@/utils/config";

// --- Interfaces ---
interface Region { id: number; region_id: string; region_name: string; }
interface District { id: number; district_id: string; district_name: string; }
interface Store { id: number; store_id: string; store_name: string; }

interface PeakTime {
  hour: string;
  orders: number;
  customers: number;
  revenue: number;
  status: string;
  trend: number;
}

interface HourlyTraffic {
  hour: string;
  orders: number;
  customers: number;
  revenue: number;
}

interface PeakHoursResponse {
  revenue: number;
  customers: number;
  peak_time: PeakTime | null;
  hourly_traffic: HourlyTraffic[];
}

export default function DashboardOverview() {
  const router = useRouter();
  const [roleId, setRoleId] = useState<number | null>(null);
  
  // User Scope extracted from JWT
  const [userScope, setUserScope] = useState({ region_id: null as number|null, district_id: null as number|null, store_id: null as number|null });

  // Data States
  const [regions, setRegions] = useState<Region[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  
  const [metrics, setMetrics] = useState({ revenue: 0, stores: 0, customers: 0 });
  const [peakData, setPeakData] = useState<PeakHoursResponse | null>(null);

  // Sales Form State
  const [salesForm, setSalesForm] = useState({ revenue: "", order_count: "", customer_count: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState("");

  const [filters, setFilters] = useState({
    region: 'all',
    district: 'all',
    store: 'all',
    date: 'last7days'
  });

  const [appliedFilters, setAppliedFilters] = useState({
    region: 'all',
    district: 'all',
    store: 'all',
    date: 'last7days'
  });

  // Fetch Lookups
  const fetchRegions = async (token: string) => {
    try {
      const res = await fetch(getApiUrl("/filters/regions"), { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setRegions(await res.json());
    } catch (e) {}
  };

  const fetchDistricts = async (token: string, regionId: string) => {
    try {
      let url = getApiUrl("/filters/districts");
      if (regionId && regionId !== 'all') url += `?region_id=${regionId}`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setDistricts(await res.json());
    } catch (e) {}
  };

  const fetchStores = async (token: string, districtId: string) => {
    try {
      let url = getApiUrl("/stores");
      if (districtId && districtId !== 'all') url += `?district_id=${districtId}&limit=1000`;
      else url += `?limit=1000`;
      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setStores(await res.json());
    } catch (e) {}
  };

  const fetchMetrics = async (filtersToUse: typeof filters) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const params = new URLSearchParams();
      if (filtersToUse.region !== 'all') params.append('region', filtersToUse.region);
      if (filtersToUse.district !== 'all') params.append('district', filtersToUse.district);
      if (filtersToUse.store !== 'all') params.append('store', filtersToUse.store);
      if (filtersToUse.date) params.append('date', filtersToUse.date);

      // Fetch basic metrics
      const resMetrics = await fetch(`${getApiUrl("/dashboard/metrics")}?${params.toString()}`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (resMetrics.ok) {
        const apiData = await resMetrics.json();
        setMetrics({ revenue: apiData.total_revenue || 0, stores: 0, customers: apiData.total_customers || 0 });
      }

      // Fetch peak hours metrics
      const resPeak = await fetch(`${getApiUrl("/dashboard/peak-hours")}?${params.toString()}`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (resPeak.ok) {
        setPeakData(await resPeak.json());
      }
    } catch (e) {
      console.error("Failed to fetch metrics", e);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const payload = JSON.parse(window.atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
        setRoleId(payload.role_id);
        setUserScope({ region_id: payload.region_id, district_id: payload.district_id, store_id: payload.store_id });
        
        if (payload.role_id === 5) {
          router.push('/dashboard/users');
          return;
        }

        fetchRegions(token);
        fetchDistricts(token, 'all');
        fetchStores(token, 'all');
      } catch (e) {}
    }
    fetchMetrics(appliedFilters);
  }, [router]);

  // Update dependent dropdowns
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) fetchDistricts(token, appliedFilters.region);
  }, [appliedFilters.region]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) fetchStores(token, appliedFilters.district);
  }, [appliedFilters.district]);

  // RBAC Locks
  const isRegionLocked = roleId === 2 || roleId === 3 || roleId === 4;
  const isDistrictLocked = roleId === 3 || roleId === 4;
  const isStoreLocked = roleId === 4;

  // Set initial filters based on scope if locked
  useEffect(() => {
    setFilters(prev => {
      let newFilters = { ...prev };
      let changed = false;
      if (isRegionLocked && userScope.region_id && prev.region === 'all') { newFilters.region = String(userScope.region_id); changed = true; }
      if (isDistrictLocked && userScope.district_id && prev.district === 'all') { newFilters.district = String(userScope.district_id); changed = true; }
      if (isStoreLocked && userScope.store_id && prev.store === 'all') { newFilters.store = String(userScope.store_id); changed = true; }
      return changed ? newFilters : prev;
    });
  }, [isRegionLocked, isDistrictLocked, isStoreLocked, userScope]);


  const handleSalesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitMessage("");
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(getApiUrl("/dashboard/sales"), {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({
          revenue: parseFloat(salesForm.revenue),
          order_count: parseInt(salesForm.order_count),
          customer_count: parseInt(salesForm.customer_count)
        })
      });
      if (res.ok) {
        setSubmitMessage("Sales submitted successfully! It may take a moment to reflect.");
        setSalesForm({ revenue: "", order_count: "", customer_count: "" });
        fetchMetrics(appliedFilters);
      } else setSubmitMessage("Failed to submit sales. Please check your inputs.");
    } catch (err) {
      setSubmitMessage("An network error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // AI Insight Logic
  const getAiInsight = () => {
    if (!peakData || !peakData.peak_time) {
      return { title: "Waiting for data", desc: "No peak hour data available.", recs: [] };
    }
    const pt = peakData.peak_time;
    return {
      title: "🔥 Peak Business Hours",
      desc: `Predicted Peak: ${pt.hour} | Expected Orders: ${pt.orders}`,
      recs: ["• Add 2 Cashiers", "• Add 1 Kitchen Staff", "• Prepare Extra Inventory", "• Increase Delivery Staff"]
    };
  };
  const insight = getAiInsight();

  // Custom Tooltip for Chart
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl">
          <p className="text-white font-semibold mb-2">{label}</p>
          <p className="text-indigo-400 text-sm">Orders: <span className="text-white">{data.orders}</span></p>
          <p className="text-emerald-400 text-sm">Revenue: <span className="text-white">${data.revenue.toLocaleString()}</span></p>
          <p className="text-purple-400 text-sm">Customers: <span className="text-white">{data.customers}</span></p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard Overview</h1>
          <p className="text-slate-400 mt-1">Here is what's happening across your locations today.</p>
        </div>
      </header>

      {/* Filter Bar */}
      <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-800/80 rounded-2xl p-4 flex flex-col xl:flex-row items-end xl:items-center justify-between gap-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-4 w-full xl:w-auto">
          {/* Region */}
          <div className="flex flex-col flex-1 min-w-[140px]">
            <label className="text-[10px] font-semibold text-slate-500 mb-1.5 uppercase tracking-widest">Region</label>
            <div className="relative">
              <select 
                disabled={isRegionLocked}
                className="w-full bg-slate-950/50 border border-slate-800 text-slate-300 text-sm rounded-xl py-2.5 pl-3 pr-8 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 focus:outline-none appearance-none transition-all cursor-pointer hover:bg-slate-900 disabled:opacity-50"
                value={filters.region} onChange={(e) => setFilters({...filters, region: e.target.value, district: 'all', store: 'all'})}
              >
                <option value="all">All Regions</option>
                {regions.map(r => <option key={r.id} value={r.id}>{r.region_name}</option>)}
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 text-xs">▼</div>
            </div>
          </div>
          {/* District */}
          <div className="flex flex-col flex-1 min-w-[140px]">
            <label className="text-[10px] font-semibold text-slate-500 mb-1.5 uppercase tracking-widest">District</label>
            <div className="relative">
              <select 
                disabled={isDistrictLocked}
                className="w-full bg-slate-950/50 border border-slate-800 text-slate-300 text-sm rounded-xl py-2.5 pl-3 pr-8 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 focus:outline-none appearance-none transition-all cursor-pointer hover:bg-slate-900 disabled:opacity-50"
                value={filters.district} onChange={(e) => setFilters({...filters, district: e.target.value, store: 'all'})}
              >
                <option value="all">All Districts</option>
                {districts.map(d => <option key={d.id} value={d.id}>{d.district_name}</option>)}
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 text-xs">▼</div>
            </div>
          </div>
          {/* Store */}
          <div className="flex flex-col flex-1 min-w-[140px]">
            <label className="text-[10px] font-semibold text-slate-500 mb-1.5 uppercase tracking-widest">Store</label>
            <div className="relative">
              <select 
                disabled={isStoreLocked}
                className="w-full bg-slate-950/50 border border-slate-800 text-slate-300 text-sm rounded-xl py-2.5 pl-3 pr-8 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 focus:outline-none appearance-none transition-all cursor-pointer hover:bg-slate-900 disabled:opacity-50"
                value={filters.store} onChange={(e) => setFilters({...filters, store: e.target.value})}
              >
                <option value="all">All Stores</option>
                {stores.map(s => <option key={s.id} value={s.store_id}>{s.store_name}</option>)}
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 text-xs">▼</div>
            </div>
          </div>
          {/* Date */}
          <div className="flex flex-col flex-1 min-w-[140px]">
            <label className="text-[10px] font-semibold text-slate-500 mb-1.5 uppercase tracking-widest">Date Range</label>
            <div className="relative">
              <select 
                className="w-full bg-slate-950/50 border border-slate-800 text-slate-300 text-sm rounded-xl py-2.5 pl-3 pr-8 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 focus:outline-none appearance-none transition-all cursor-pointer hover:bg-slate-900"
                value={filters.date} onChange={(e) => setFilters({...filters, date: e.target.value})}
              >
                <option value="today">Today</option>
                <option value="yesterday">Yesterday</option>
                <option value="last7days">Last 7 Days</option>
                <option value="lastmonth">Last Month</option>
              </select>
              <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500 text-xs">▼</div>
            </div>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-3 w-full xl:w-auto">
          <button 
            onClick={() => {
              setFilters(prev => {
                const defaults = { 
                  region: isRegionLocked ? prev.region : 'all', 
                  district: isDistrictLocked ? prev.district : 'all', 
                  store: isStoreLocked ? prev.store : 'all', 
                  date: 'last7days' 
                };
                setAppliedFilters(defaults);
                fetchMetrics(defaults);
                return defaults;
              });
            }}
            className="flex-1 xl:flex-none px-5 py-2.5 text-sm font-medium text-slate-300 bg-slate-800/50 hover:bg-slate-700/80 rounded-xl transition-all border border-slate-700/50 hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-500"
          >
            Reset
          </button>
          <button 
            onClick={() => {
              setAppliedFilters(filters);
              fetchMetrics(filters);
            }}
            className="flex-1 xl:flex-none px-6 py-2.5 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 rounded-xl transition-all shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900"
          >
            Apply Filters
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Revenue Card */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-indigo-500/50 transition-colors">
          <div className="absolute top-0 right-0 p-4 opacity-10 transform translate-x-4 -translate-y-4 group-hover:scale-110 transition-transform">
            <DollarSign className="w-24 h-24 text-indigo-400" />
          </div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-sm font-medium text-slate-400">Total Revenue</p>
              <p className="text-3xl font-bold text-white mt-2">${metrics.revenue.toLocaleString()}</p>
            </div>
            <div className="p-2 bg-indigo-500/20 rounded-lg">
              <DollarSign className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
        </div>

        {/* Customers Card */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-purple-500/50 transition-colors">
          <div className="absolute top-0 right-0 p-4 opacity-10 transform translate-x-4 -translate-y-4 group-hover:scale-110 transition-transform">
            <Users className="w-24 h-24 text-purple-400" />
          </div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-sm font-medium text-slate-400">Active Customers</p>
              <p className="text-3xl font-bold text-white mt-2">{metrics.customers.toLocaleString()}</p>
            </div>
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Users className="w-5 h-5 text-purple-400" />
            </div>
          </div>
        </div>

        {/* Peak Business Hours Card */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-amber-800/40 rounded-2xl p-6 relative overflow-hidden group hover:border-amber-500/50 transition-colors">
          <div className="absolute top-0 right-0 p-4 opacity-10 transform translate-x-4 -translate-y-4 group-hover:scale-110 transition-transform">
            <Clock className="w-24 h-24 text-amber-400" />
          </div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-sm font-medium text-slate-400">Peak Business Hours</p>
              <p className="text-xl font-bold text-white mt-2">
                {peakData?.peak_time ? peakData.peak_time.hour : "N/A"}
              </p>
              {peakData?.peak_time && (
                <div className="mt-2 text-sm text-slate-300">
                  <span className="font-semibold text-amber-400">{peakData.peak_time.status}</span>
                  <span className="mx-2">•</span>
                  <span>{peakData.peak_time.orders} Orders</span>
                </div>
              )}
            </div>
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <Clock className="w-5 h-5 text-amber-400" />
            </div>
          </div>
          {peakData?.peak_time && (
            <div className="mt-4 flex items-center text-sm">
              <span className="text-emerald-400 flex items-center font-medium">
                <ArrowUpRight className="w-4 h-4 mr-1" /> +{peakData.peak_time.trend}%
              </span>
              <span className="text-slate-500 ml-2">from yesterday</span>
            </div>
          )}
        </div>

        {/* Performance Card */}
        <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-6 relative overflow-hidden shadow-xl shadow-indigo-500/20">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10" />
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-sm font-medium text-indigo-100">{insight.title}</p>
              <p className="text-lg font-bold text-white mt-2 leading-tight">
                {insight.desc}
              </p>
            </div>
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-white/20 relative z-10 flex flex-col gap-1">
            {insight.recs.map((r, i) => <p key={i} className="text-xs text-indigo-100">{r}</p>)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Customer Traffic by Hour Chart Section */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 lg:col-span-3">
          <h2 className="text-lg font-bold text-white mb-6">Customer Traffic by Hour</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={peakData?.hourly_traffic || []} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorOrders" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.5}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="hour" stroke="#475569" tick={{fill: '#94a3b8'}} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" tick={{fill: '#94a3b8'}} tickLine={false} axisLine={false} />
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="orders" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorOrders)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Store Manager Sales Input Form */}
        {roleId === 4 && (
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 flex flex-col lg:col-span-3">
            <h2 className="text-lg font-bold text-white mb-1">Submit Daily Sales</h2>
            <p className="text-sm text-slate-400 mb-6">Enter today's totals for your store.</p>
            
            {submitMessage && (
              <div className={`p-3 rounded-lg text-sm mb-4 ${submitMessage.includes("success") ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-red-500/20 text-red-300 border border-red-500/30"}`}>
                {submitMessage}
              </div>
            )}

            <form onSubmit={handleSalesSubmit} className="space-y-4 flex-1 max-w-xl">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Total Revenue ($)</label>
                <input 
                  type="number" step="0.01" required value={salesForm.revenue}
                  onChange={(e) => setSalesForm({...salesForm, revenue: e.target.value})}
                  className="w-full bg-slate-800/50 border border-slate-700 text-white rounded-xl py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none placeholder:text-slate-500" 
                  placeholder="e.g. 1250.50" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Number of Orders</label>
                <input 
                  type="number" required value={salesForm.order_count}
                  onChange={(e) => setSalesForm({...salesForm, order_count: e.target.value})}
                  className="w-full bg-slate-800/50 border border-slate-700 text-white rounded-xl py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none placeholder:text-slate-500" 
                  placeholder="e.g. 45" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Number of Customers</label>
                <input 
                  type="number" required value={salesForm.customer_count}
                  onChange={(e) => setSalesForm({...salesForm, customer_count: e.target.value})}
                  className="w-full bg-slate-800/50 border border-slate-700 text-white rounded-xl py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none placeholder:text-slate-500" 
                  placeholder="e.g. 120" 
                />
              </div>
              
              <button 
                type="submit" disabled={isSubmitting}
                className="w-full mt-auto py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-colors disabled:opacity-50"
              >
                {isSubmitting ? "Submitting..." : "Submit Totals"}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

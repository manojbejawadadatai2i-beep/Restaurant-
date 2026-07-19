"use client";

import { useEffect, useState } from "react";
import { TrendingUp, Users, DollarSign, ArrowUpRight } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

import { getApiUrl } from "@/config";

const data = [
  { name: "Mon", revenue: 4000, customers: 240 },
  { name: "Tue", revenue: 3000, customers: 139 },
  { name: "Wed", revenue: 2000, customers: 980 },
  { name: "Thu", revenue: 2780, customers: 390 },
  { name: "Fri", revenue: 1890, customers: 480 },
  { name: "Sat", revenue: 2390, customers: 380 },
  { name: "Sun", revenue: 3490, customers: 430 },
];

export default function DashboardOverview() {
  const [metrics, setMetrics] = useState({ revenue: 0, stores: 0, customers: 0 });
  const [roleId, setRoleId] = useState<string | null>(null);

  // Sales Form State
  const [salesForm, setSalesForm] = useState({ revenue: "", order_count: "", customer_count: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState("");

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const token = localStorage.getItem("token");
        if (token) {
          try {
            const payload = JSON.parse(window.atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
            setRoleId(payload.role_id);
          } catch (e) {}
        }

        const res = await fetch(getApiUrl("/dashboard/metrics"), {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        
        if (res.ok) {
          const apiData = await res.json();
          // The metrics endpoint returns an object like {total_revenue: 0, total_customers: 0, total_orders: 0}
          if (apiData) {
            setMetrics({ 
              revenue: apiData.total_revenue || 0, 
              stores: 0, 
              customers: apiData.total_customers || 0 
            });
            return;
          }
        }
      } catch (e) {
        console.error("Failed to fetch metrics", e);
      }
      
      // Fallback data if DB is empty or call fails
      setMetrics({ revenue: 42500, stores: 12, customers: 8940 });
    };

    fetchMetrics();
  }, []);

  const handleSalesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitMessage("");
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(getApiUrl("/dashboard/sales"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          revenue: parseFloat(salesForm.revenue),
          order_count: parseInt(salesForm.order_count),
          customer_count: parseInt(salesForm.customer_count)
        })
      });
      if (res.ok) {
        setSubmitMessage("Sales submitted successfully! It may take a moment to reflect.");
        setSalesForm({ revenue: "", order_count: "", customer_count: "" });
      } else {
        setSubmitMessage("Failed to submit sales. Please check your inputs.");
      }
    } catch (err) {
      setSubmitMessage("An network error occurred.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Dashboard Overview</h1>
        <p className="text-slate-400 mt-1">Here is what's happening across your regions today.</p>
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
          <div className="mt-4 flex items-center text-sm">
            <span className="text-emerald-400 flex items-center font-medium">
              <ArrowUpRight className="w-4 h-4 mr-1" /> +12.5%
            </span>
            <span className="text-slate-500 ml-2">from last month</span>
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
          <div className="mt-4 flex items-center text-sm">
            <span className="text-emerald-400 flex items-center font-medium">
              <ArrowUpRight className="w-4 h-4 mr-1" /> +5.2%
            </span>
            <span className="text-slate-500 ml-2">from last month</span>
          </div>
        </div>

        {/* Performance Card */}
        <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-2xl p-6 relative overflow-hidden shadow-xl shadow-indigo-500/20">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10" />
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-sm font-medium text-indigo-100">AI Performance Insight</p>
              <p className="text-xl font-bold text-white mt-2 leading-tight">
                Store #42 is predicted to peak at 7 PM tonight. Consider adjusting staff.
              </p>
            </div>
            <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-white/20 relative z-10">
            <button className="text-sm font-medium text-white hover:text-indigo-200 transition-colors">
              View full AI report &rarr;
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Section */}
        <div className={`bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 ${roleId === 'RL04' ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
          <h2 className="text-lg font-bold text-white mb-6">Revenue Trend (Last 7 Days)</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.5}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#475569" tick={{fill: '#94a3b8'}} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" tick={{fill: '#94a3b8'}} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '0.75rem', color: '#f8fafc' }}
                  itemStyle={{ color: '#818cf8' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#818cf8" strokeWidth={3} fillOpacity={1} fill="url(#colorRevenue)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Store Manager Sales Input Form */}
        {roleId === "RL04" && (
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 flex flex-col">
            <h2 className="text-lg font-bold text-white mb-1">Submit Daily Sales</h2>
            <p className="text-sm text-slate-400 mb-6">Enter today's totals for your store.</p>
            
            {submitMessage && (
              <div className={`p-3 rounded-lg text-sm mb-4 ${submitMessage.includes("success") ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-red-500/20 text-red-300 border border-red-500/30"}`}>
                {submitMessage}
              </div>
            )}

            <form onSubmit={handleSalesSubmit} className="space-y-4 flex-1">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Total Revenue ($)</label>
                <input 
                  type="number" 
                  step="0.01"
                  required
                  value={salesForm.revenue}
                  onChange={(e) => setSalesForm({...salesForm, revenue: e.target.value})}
                  className="w-full bg-slate-800/50 border border-slate-700 text-white rounded-xl py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none placeholder:text-slate-500" 
                  placeholder="e.g. 1250.50" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Number of Orders</label>
                <input 
                  type="number" 
                  required
                  value={salesForm.order_count}
                  onChange={(e) => setSalesForm({...salesForm, order_count: e.target.value})}
                  className="w-full bg-slate-800/50 border border-slate-700 text-white rounded-xl py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none placeholder:text-slate-500" 
                  placeholder="e.g. 45" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Number of Customers</label>
                <input 
                  type="number" 
                  required
                  value={salesForm.customer_count}
                  onChange={(e) => setSalesForm({...salesForm, customer_count: e.target.value})}
                  className="w-full bg-slate-800/50 border border-slate-700 text-white rounded-xl py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:outline-none placeholder:text-slate-500" 
                  placeholder="e.g. 120" 
                />
              </div>
              
              <button 
                type="submit" 
                disabled={isSubmitting}
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

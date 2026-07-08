"use client";

import { useEffect, useState } from "react";
import { PieChart, TrendingUp, DollarSign, Users, ShoppingCart } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Sale {
  sale_id: string;
  store_id: string;
  revenue: number;
  order_count: number;
  customer_count: number;
  sale_date: string;
}

export default function ReportsPage() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSales = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/dashboard/sales", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setSales(data);
        }
      } catch (e) {
        console.error("Failed to fetch sales", e);
      } finally {
        setLoading(false);
      }
    };
    fetchSales();
  }, []);

  const totalRevenue = sales.reduce((acc, s) => acc + (Number(s.revenue) || 0), 0);
  const totalCustomers = sales.reduce((acc, s) => acc + (s.customer_count || 0), 0);
  const totalOrders = sales.reduce((acc, s) => acc + (s.order_count || 0), 0);

  // Group by store for chart
  const chartData = Object.values(
    sales.reduce((acc: Record<string, any>, s) => {
      const key = s.store_id;
      if (!acc[key]) acc[key] = { store: key, revenue: 0, orders: 0 };
      acc[key].revenue += Number(s.revenue) || 0;
      acc[key].orders += s.order_count || 0;
      return acc;
    }, {})
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Performance Reports</h1>
        <p className="text-slate-400 mt-1">Sales and customer metrics across all stores.</p>
      </header>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-emerald-500/10 rounded-lg"><DollarSign className="w-5 h-5 text-emerald-400" /></div>
            <span className="text-slate-400 text-sm font-medium">Total Revenue</span>
          </div>
          <p className="text-4xl font-bold text-white">${totalRevenue.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/10 rounded-lg"><Users className="w-5 h-5 text-purple-400" /></div>
            <span className="text-slate-400 text-sm font-medium">Total Customers</span>
          </div>
          <p className="text-4xl font-bold text-white">{totalCustomers.toLocaleString()}</p>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-amber-500/10 rounded-lg"><ShoppingCart className="w-5 h-5 text-amber-400" /></div>
            <span className="text-slate-400 text-sm font-medium">Total Orders</span>
          </div>
          <p className="text-4xl font-bold text-white">{totalOrders.toLocaleString()}</p>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-indigo-400" /> Revenue by Store
        </h2>
        {loading ? (
          <div className="text-slate-400 text-center py-16">Loading data...</div>
        ) : chartData.length === 0 ? (
          <div className="text-center py-16">
            <PieChart className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No sales data found.</p>
          </div>
        ) : (
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="store" stroke="#475569" tick={{ fill: "#94a3b8" }} tickLine={false} axisLine={false} />
                <YAxis stroke="#475569" tick={{ fill: "#94a3b8" }} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "0.75rem", color: "#f8fafc" }}
                  formatter={(v) => [`$${Number(v ?? 0).toLocaleString()}`, "Revenue"] as [string, string]}
                />
                <Bar dataKey="revenue" fill="#818cf8" radius={[6, 6, 0, 0]} name="Revenue ($)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Sales Table */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800">
          <h2 className="text-lg font-bold text-white">Recent Sales Records</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left text-slate-400 font-medium px-6 py-3">Sale ID</th>
                <th className="text-left text-slate-400 font-medium px-6 py-3">Store</th>
                <th className="text-left text-slate-400 font-medium px-6 py-3">Revenue</th>
                <th className="text-left text-slate-400 font-medium px-6 py-3">Orders</th>
                <th className="text-left text-slate-400 font-medium px-6 py-3">Customers</th>
                <th className="text-left text-slate-400 font-medium px-6 py-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {sales.slice(0, 10).map((s) => (
                <tr key={s.sale_id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-3 text-slate-400 font-mono text-xs">{s.sale_id}</td>
                  <td className="px-6 py-3 text-white font-medium">{s.store_id}</td>
                  <td className="px-6 py-3 text-emerald-400 font-semibold">${Number(s.revenue).toLocaleString()}</td>
                  <td className="px-6 py-3 text-slate-300">{s.order_count}</td>
                  <td className="px-6 py-3 text-slate-300">{s.customer_count}</td>
                  <td className="px-6 py-3 text-slate-400">{s.sale_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

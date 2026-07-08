"use client";

import { useEffect, useState } from "react";
import { Users, Search, ShieldCheck } from "lucide-react";

interface UserData {
  user_id: string;
  full_name: string;
  email: string;
  role_id: string;
  is_active: boolean;
}

const roleLabel: Record<string, string> = {
  RL01: "Corporate Administrator",
  RL02: "Regional Manager",
  RL03: "District Manager",
  RL04: "Store Manager",
};

const roleColors: Record<string, string> = {
  RL01: "bg-purple-500/20 text-purple-300 border border-purple-500/30",
  RL02: "bg-blue-500/20 text-blue-300 border border-blue-500/30",
  RL03: "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
  RL04: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
};

export default function TeamPage() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/users/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setUsers(data || []);
        }
      } catch (e) {
        console.error("Failed to fetch users", e);
      } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  const filtered = users.filter(
    (u) =>
      u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight">Team</h1>
        <p className="text-slate-400 mt-1">All users and their assigned roles.</p>
      </header>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search team members..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-900/50 border border-slate-700 text-slate-200 rounded-xl py-2.5 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm placeholder:text-slate-500"
        />
      </div>

      {loading ? (
        <div className="text-slate-400 text-center py-20">Loading team...</div>
      ) : (
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left text-slate-400 font-medium px-6 py-4">User</th>
                <th className="text-left text-slate-400 font-medium px-6 py-4">Email</th>
                <th className="text-left text-slate-400 font-medium px-6 py-4">Role</th>
                <th className="text-left text-slate-400 font-medium px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((user) => (
                <tr key={user.user_id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                        {user.full_name?.charAt(0) || "?"}
                      </div>
                      <div>
                        <p className="font-medium text-white">{user.full_name || "Unknown"}</p>
                        <p className="text-slate-500 text-xs font-mono">{user.user_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${roleColors[user.role_id] || "bg-slate-700 text-slate-300"}`}>
                      <ShieldCheck className="w-3 h-3" />
                      {roleLabel[user.role_id] || user.role_id}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${user.is_active ? "bg-emerald-500/10 text-emerald-400" : "bg-slate-700 text-slate-400"}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${user.is_active ? "bg-emerald-400" : "bg-slate-400"}`} />
                      {user.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

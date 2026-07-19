"use client";

import { useEffect, useState } from "react";
import { Search, ShieldCheck, CheckCircle2, AlertCircle, X, UserPlus } from "lucide-react";

import { getApiUrl } from "@/config";

interface UserData {
  id: number;
  employee_id: string;
  full_name: string;
  email: string;
  role_id: number;
  is_active: boolean;
  region_id?: number;
  district_id?: number;
  store_id?: number;
  corporate_id?: number;
}

const roleLabel: Record<number, string> = {
  1: "Corporate Administrator",
  2: "Regional Manager",
  3: "District Manager",
  4: "Store Manager",
};

const roleColors: Record<number, string> = {
  1: "bg-purple-500/20 text-purple-300 border border-purple-500/30",
  2: "bg-blue-500/20 text-blue-300 border border-blue-500/30",
  3: "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
  4: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
};

export default function TeamPage() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [currentUserRole, setCurrentUserRole] = useState<number>(0);

  // Approval Modal State
  const [approvingUser, setApprovingUser] = useState<UserData | null>(null);
  const [regions, setRegions] = useState<any[]>([]);
  const [districts, setDistricts] = useState<any[]>([]);
  const [stores, setStores] = useState<any[]>([]);
  
  // Add User State
  const [isAddingUser, setIsAddingUser] = useState(false);
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserRole, setNewUserRole] = useState(4);
  const [newUserPassword, setNewUserPassword] = useState("");
  const [addError, setAddError] = useState("");
  
  const [selectedRegion, setSelectedRegion] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [selectedStore, setSelectedStore] = useState("");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setCurrentUserRole(payload.role_id);
        } catch (e) {
          console.error("Failed to decode token", e);
        }
      }

      const [usersRes, regRes, distRes, storeRes] = await Promise.all([
        fetch(getApiUrl("/users/"), { headers: { Authorization: `Bearer ${token}` } }),
        fetch(getApiUrl("/regions"), { headers: { Authorization: `Bearer ${token}` } }),
        fetch(getApiUrl("/districts"), { headers: { Authorization: `Bearer ${token}` } }),
        fetch(getApiUrl("/stores/"), { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      
      if (usersRes.ok) setUsers(await usersRes.json() || []);
      if (regRes.ok) setRegions(await regRes.json() || []);
      if (distRes.ok) setDistricts(await distRes.json() || []);
      if (storeRes.ok) setStores(await storeRes.json() || []);
    } catch (e) {
      console.error("Failed to fetch users", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!approvingUser) {
      setSelectedRegion("");
      setSelectedDistrict("");
      setSelectedStore("");
    }
  }, [approvingUser]);

  const confirmApprove = async () => {
    if (!approvingUser) return;
    
    try {
      const token = localStorage.getItem("token");
      
      const payload: any = { is_active: true };
      if (selectedRegion) payload.region_id = parseInt(selectedRegion);
      if (selectedDistrict) payload.district_id = parseInt(selectedDistrict);
      if (selectedStore) payload.store_id = parseInt(selectedStore);

      const res = await fetch(getApiUrl(`/users/${approvingUser.employee_id}`), {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      
      if (res.ok) {
        setUsers(users.map(u => 
          u.employee_id === approvingUser.employee_id 
            ? { ...u, is_active: true, ...payload } 
            : u
        ));
        setApprovingUser(null);
      }
    } catch (e) {
      console.error("Failed to approve user", e);
    }
  };

  const filtered = users.filter(
    (u) =>
      u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
  );
  
  const filteredDistricts = districts.filter(d => !selectedRegion || String(d.region_id) === selectedRegion);
  const filteredStores = stores.filter(s => !selectedDistrict || String(s.district_id) === selectedDistrict);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 relative">
      <header className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-white tracking-tight">Team</h1>
            {users.filter(u => !u.is_active).length > 0 && (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse">
                {users.filter(u => !u.is_active).length} Pending
              </span>
            )}
          </div>
          <p className="text-slate-400 mt-1">All users and their assigned roles.</p>
        </div>
        <div className="flex gap-3">
          {(currentUserRole === 1 || currentUserRole === 5) && (
            <button
              onClick={() => setIsAddingUser(true)}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white border border-indigo-500 rounded-xl text-sm font-medium transition-colors shadow-lg shadow-indigo-500/20"
            >
              <UserPlus className="w-4 h-4" />
              Add User
            </button>
          )}
          <button
            onClick={fetchUsers}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 rounded-xl text-sm font-medium transition-colors"
          >
            ↻ Refresh
          </button>
        </div>>
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
                <th className="text-left text-slate-400 font-medium px-6 py-4">Location</th>
                <th className="text-left text-slate-400 font-medium px-6 py-4">Status</th>
                <th className="text-right text-slate-400 font-medium px-6 py-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((user) => {
                const storeName = stores.find(s => s.store_id === user.store_id)?.name || stores.find(s => s.store_id === user.store_id)?.store_name;
                const districtName = districts.find(d => d.district_id === user.district_id)?.name || districts.find(d => d.district_id === user.district_id)?.district_name;
                const regionName = regions.find(r => r.region_id === user.region_id)?.name || regions.find(r => r.region_id === user.region_id)?.region_name;
                
                const locationText = storeName || districtName || regionName || "Unassigned";

                return (
                  <tr key={user.id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                        {user.full_name?.charAt(0) || "?"}
                      </div>
                      <div>
                        <p className="font-medium text-white">{user.full_name || "Unknown"}</p>
                        <p className="text-slate-500 text-xs font-mono">{user.employee_id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-300">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${roleColors[user.role_id] || "bg-slate-700 text-slate-300"}`}>
                      <ShieldCheck className="w-3 h-3" />
                      {roleLabel[user.role_id] || `Role ${user.role_id}`}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-slate-300 text-sm">{locationText}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${user.is_active ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${user.is_active ? "bg-emerald-400" : "bg-amber-400"}`} />
                      {user.is_active ? "Active" : "Pending"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {!user.is_active && currentUserRole === 1 && (
                      <button
                        onClick={() => setApprovingUser(user)}
                        className="px-3 py-1 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-lg text-xs font-medium hover:bg-indigo-500/40 transition-colors"
                      >
                        Approve
                      </button>
                    )}
                  </td>
                </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

        </div>
      )}

      {/* Add User Modal */}
      {isAddingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">Add New User</h3>
              <button onClick={() => { setIsAddingUser(false); setAddError(""); }} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {addError && (
              <div className="bg-red-500/20 border border-red-500/50 text-red-200 p-3 rounded-lg text-sm mb-6 text-center">
                {addError}
              </div>
            )}

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Full Name</label>
                <input 
                  type="text"
                  value={newUserName}
                  onChange={e => setNewUserName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="John Doe"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Email</label>
                <input 
                  type="email"
                  value={newUserEmail}
                  onChange={e => setNewUserEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="john@restaurant.com"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Password</label>
                <input 
                  type="text"
                  value={newUserPassword}
                  onChange={e => setNewUserPassword(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Default password"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Role</label>
                <select 
                  value={newUserRole} 
                  onChange={(e) => {
                    setNewUserRole(parseInt(e.target.value));
                  }}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value={1}>Corporate Administrator</option>
                  <option value={2}>Regional Manager</option>
                  <option value={3}>District Manager</option>
                  <option value={4}>Store Manager</option>
                  <option value={5}>User Admin</option>
                </select>
              </div>

              {/* Location Assignments */}
              <div className="space-y-1.5 pt-2 border-t border-slate-800">
                <label className="text-sm font-medium text-slate-300">Assign Region (Optional)</label>
                <select 
                  value={selectedRegion} 
                  onChange={(e) => {
                    setSelectedRegion(e.target.value);
                    setSelectedDistrict("");
                    setSelectedStore("");
                  }}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- No Region --</option>
                  {regions.map(r => (
                    <option key={r.region_id} value={r.region_id}>{r.region_name}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign District (Optional)</label>
                <select 
                  value={selectedDistrict} 
                  onChange={(e) => {
                    setSelectedDistrict(e.target.value);
                    setSelectedStore("");
                  }}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- No District --</option>
                  {filteredDistricts.map(d => (
                    <option key={d.district_id} value={d.district_id}>{d.district_name}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign Store (Optional)</label>
                <select 
                  value={selectedStore} 
                  onChange={(e) => setSelectedStore(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- No Store --</option>
                  {filteredStores.map(s => (
                    <option key={s.store_id} value={s.store_id}>{s.name || s.store_name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mt-8 flex gap-3">
              <button 
                onClick={() => { setIsAddingUser(false); setAddError(""); }}
                className="flex-1 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={async () => {
                  setAddError("");
                  if (!newUserName || !newUserEmail || !newUserPassword) {
                    setAddError("Name, email, and password are required.");
                    return;
                  }
                  try {
                    const token = localStorage.getItem("token");
                    const payload: any = { 
                      full_name: newUserName,
                      email: newUserEmail,
                      password: newUserPassword,
                      role_id: newUserRole,
                      is_active: true
                    };
                    if (selectedRegion) payload.region_id = parseInt(selectedRegion);
                    if (selectedDistrict) payload.district_id = parseInt(selectedDistrict);
                    if (selectedStore) payload.store_id = parseInt(selectedStore);

                    const res = await fetch(getApiUrl("/users/"), {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                      },
                      body: JSON.stringify(payload),
                    });
                    
                    if (res.ok) {
                      setIsAddingUser(false);
                      setNewUserName("");
                      setNewUserEmail("");
                      setNewUserPassword("");
                      setSelectedRegion("");
                      setSelectedDistrict("");
                      setSelectedStore("");
                      fetchUsers(); // Refresh list
                    } else {
                      const err = await res.json();
                      setAddError(err.detail || "Failed to create user");
                    }
                  } catch (e) {
                    setAddError("Network error occurred");
                  }
                }}
                className="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium shadow-lg shadow-indigo-500/20 transition-colors"
              >
                Create User
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Approval Modal */}
      {approvingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">Approve User</h3>
              <button onClick={() => setApprovingUser(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-slate-400 mb-1">Approving access for:</p>
              <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl">
                 <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    {approvingUser.full_name?.charAt(0) || "?"}
                  </div>
                  <div>
                    <p className="font-medium text-white">{approvingUser.full_name}</p>
                    <p className="text-slate-400 text-xs">{roleLabel[approvingUser.role_id] || `Role ${approvingUser.role_id}`}</p>
                  </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign Region (Optional)</label>
                <select 
                  value={selectedRegion} 
                  onChange={(e) => {
                    setSelectedRegion(e.target.value);
                    setSelectedDistrict("");
                    setSelectedStore("");
                  }}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- No Region --</option>
                  {regions.map(r => (
                    <option key={r.region_id} value={r.region_id}>{r.region_name}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign District (Optional)</label>
                <select 
                  value={selectedDistrict} 
                  onChange={(e) => {
                    setSelectedDistrict(e.target.value);
                    setSelectedStore("");
                  }}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- No District --</option>
                  {filteredDistricts.map(d => (
                    <option key={d.district_id} value={d.district_id}>{d.district_name}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign Store (Optional)</label>
                <select 
                  value={selectedStore} 
                  onChange={(e) => setSelectedStore(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">-- No Store --</option>
                  {filteredStores.map(s => (
                    <option key={s.store_id} value={s.store_id}>{s.store_name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <button 
                onClick={() => setApprovingUser(null)}
                className="px-4 py-2 text-slate-300 hover:text-white font-medium transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={confirmApprove}
                className="px-6 py-2 bg-indigo-500 hover:bg-indigo-400 text-white rounded-xl font-medium shadow-lg shadow-indigo-500/20 transition-all"
              >
                Confirm Approval
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { Search, ShieldCheck, CheckCircle2, X, UserPlus, ChevronDown } from "lucide-react";

import { getApiUrl } from "@/utils/config";

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
  5: "User Admin",
};

const roleColors: Record<number, string> = {
  1: "bg-purple-500/20 text-purple-300 border border-purple-500/30",
  2: "bg-blue-500/20 text-blue-300 border border-blue-500/30",
  3: "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
  4: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
  5: "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30",
};

// Roles a User Admin can assign (Corporate Admin excluded)
const ASSIGNABLE_ROLES = [
  { id: 2, label: "Region" },
  { id: 3, label: "District" },
  { id: 4, label: "Store" },
];

// Which location fields are required per role
function getRequiredFields(roleId: number) {
  if (roleId === 2) return { region: true, district: false, store: false };
  if (roleId === 3) return { region: true, district: true, store: false };
  if (roleId === 4) return { region: true, district: true, store: true };
  return { region: false, district: false, store: false };
}

const selectCls = (disabled?: boolean) =>
  `w-full bg-slate-950 border ${
    disabled ? "border-slate-800 opacity-50 cursor-not-allowed" : "border-slate-700"
  } text-white rounded-xl py-2.5 px-4 pr-10 focus:outline-none focus:ring-2 focus:ring-indigo-500 appearance-none transition-opacity`;

export default function TeamPage() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [currentUserRole, setCurrentUserRole] = useState<number>(0);

  const [regions, setRegions] = useState<any[]>([]);
  const [allDistricts, setAllDistricts] = useState<any[]>([]);
  const [allStores, setAllStores] = useState<any[]>([]);

  // Add User State
  const [isAddingUser, setIsAddingUser] = useState(false);
  const [newUserName, setNewUserName] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserRole, setNewUserRole] = useState(4);
  const [addError, setAddError] = useState("");
  const [addLoading, setAddLoading] = useState(false);
  const [generatedPassInfo, setGeneratedPassInfo] = useState<{ name: string; pass: string } | null>(null);

  const [selectedRegion, setSelectedRegion] = useState("");
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [selectedStore, setSelectedStore] = useState("");

  // New Store inline form
  const [isCreatingNewStore, setIsCreatingNewStore] = useState(false);
  const [newStoreName, setNewStoreName] = useState("");
  const [newStoreCity, setNewStoreCity] = useState("");
  const [newStoreAddress, setNewStoreAddress] = useState("");

  // Approval Modal State
  const [approvingUser, setApprovingUser] = useState<UserData | null>(null);
  const [approveRegion, setApproveRegion] = useState("");
  const [approveDistrict, setApproveDistrict] = useState("");
  const [approveStore, setApproveStore] = useState("");

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split(".")[1]));
          setCurrentUserRole(payload.role_id);
        } catch {}
      }
      const [usersRes, regRes, distRes, storeRes] = await Promise.all([
        fetch(getApiUrl("/users"), { headers: { Authorization: `Bearer ${token}` } }),
        fetch(getApiUrl("/regions"), { headers: { Authorization: `Bearer ${token}` } }),
        fetch(getApiUrl("/districts?limit=1000"), { headers: { Authorization: `Bearer ${token}` } }),
        fetch(getApiUrl("/stores?limit=1000"), { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (usersRes.ok) setUsers((await usersRes.json()) || []);
      if (regRes.ok) setRegions((await regRes.json()) || []);
      if (distRes.ok) setAllDistricts((await distRes.json()) || []);
      if (storeRes.ok) setAllStores((await storeRes.json()) || []);
    } catch {}
    finally {
      setLoading(false);
    }
  };

  // Identify stores already assigned to a real user (with an email) for the selected role
  const assignedStoreIds = users
    .filter((u) => u.role_id === newUserRole && u.store_id && u.email && u.email.trim() !== "")
    .map((u) => String(u.store_id));

  // Cascaded filtering for Add User modal
  const filteredDistricts = allDistricts.filter(
    (d) => selectedRegion && String(d.region_id) === selectedRegion
  );
  const filteredStores = allStores.filter(
    (s) => selectedDistrict && String(s.district_id) === selectedDistrict && !assignedStoreIds.includes(String(s.id))
  );

  const globallyAvailableStores = allStores.filter(
    (s) => !assignedStoreIds.includes(String(s.id))
  );

  // Cascaded filtering for Approval modal
  const approveFilteredDistricts = allDistricts.filter(
    (d) => approveRegion && String(d.region_id) === approveRegion
  );
  const approveFilteredStores = allStores.filter(
    (s) => approveDistrict && String(s.district_id) === approveDistrict
  );

  const requiredFields = getRequiredFields(newUserRole);

  const resetAddForm = () => {
    setNewUserName("");
    setNewUserEmail("");
    setNewUserRole(4);
    setSelectedRegion("");
    setSelectedDistrict("");
    setSelectedStore("");
    setIsCreatingNewStore(false);
    setNewStoreName("");
    setNewStoreCity("");
    setNewStoreAddress("");
    setAddError("");
    setGeneratedPassInfo(null);
    setAddLoading(false);
  };

  const handleCreateUser = async () => {
    setAddError("");
    if (!newUserName.trim()) {
      setAddError("Full name is required.");
      return;
    }
    if (!newUserEmail.trim()) {
      setAddError("Email is required.");
      return;
    }
    if (requiredFields.store && !selectedStore && !isCreatingNewStore) {
      setAddError("Please select a store, create a new one, or leave unassigned.");
      return;
    }
    
    const isUnassignedStore = selectedStore === "unassigned";

    if (requiredFields.region && !selectedRegion && !isUnassignedStore) {
      setAddError("Please select a region for this role.");
      return;
    }
    if (requiredFields.district && !selectedDistrict && !isUnassignedStore) {
      setAddError("Please select a district for this role.");
      return;
    }
    if (isCreatingNewStore && !newStoreName.trim()) {
      setAddError("New store name is required.");
      return;
    }

    setAddLoading(true);
    try {
      const token = localStorage.getItem("token");
      let resolvedStoreId = selectedStore && selectedStore !== "unassigned" ? parseInt(selectedStore) : undefined;

      // If creating a new store first
      if (isCreatingNewStore && selectedDistrict) {
        const storeRes = await fetch(getApiUrl("/stores"), {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({
            store_name: newStoreName.trim(),
            district_id: parseInt(selectedDistrict),
            city: newStoreCity.trim() || undefined,
            address: newStoreAddress.trim() || undefined,
          }),
        });
        if (!storeRes.ok) {
          const err = await storeRes.json();
          setAddError(err.detail || "Failed to create store.");
          setAddLoading(false);
          return;
        }
        const newStore = await storeRes.json();
        // Refresh stores list
        const updatedStores = await fetch(getApiUrl("/stores?limit=1000"), {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (updatedStores.ok) setAllStores(await updatedStores.json());
        resolvedStoreId = newStore.id;
      }

      const payload: any = {
        full_name: newUserName.trim(),
        email: newUserEmail.trim(),
        role_id: newUserRole,
        is_active: true,
      };
      if (selectedRegion) payload.region_id = parseInt(selectedRegion);
      if (selectedDistrict) payload.district_id = parseInt(selectedDistrict);
      if (resolvedStoreId) payload.store_id = resolvedStoreId;

      const res = await fetch(getApiUrl("/users"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setGeneratedPassInfo({ name: data.full_name, pass: data.generated_password });
        fetchUsers();
      } else {
        const err = await res.json();
        setAddError(err.detail || "Failed to create user.");
      }
    } catch {
      setAddError("Network error. Please try again.");
    } finally {
      setAddLoading(false);
    }
  };

  const confirmApprove = async () => {
    if (!approvingUser) return;
    try {
      const token = localStorage.getItem("token");
      const payload: any = { is_active: true };
      if (approveRegion) payload.region_id = parseInt(approveRegion);
      if (approveDistrict) payload.district_id = parseInt(approveDistrict);
      if (approveStore) payload.store_id = parseInt(approveStore);

      const res = await fetch(getApiUrl(`/users/${approvingUser.employee_id}`), {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setUsers(
          users.map((u) =>
            u.employee_id === approvingUser.employee_id
              ? { ...u, is_active: true, ...payload }
              : u
          )
        );
        setApprovingUser(null);
        setApproveRegion("");
        setApproveDistrict("");
        setApproveStore("");
      }
    } catch {}
  };

  const filtered = users.filter(
    (u) =>
      u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 relative">
      {/* Page Header */}
      <header className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-white tracking-tight">Team</h1>
            {users.filter((u) => !u.is_active).length > 0 && (
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse">
                {users.filter((u) => !u.is_active).length} Pending
              </span>
            )}
          </div>
          <p className="text-slate-400 mt-1">All users and their assigned roles.</p>
        </div>
        <div className="flex gap-3">
          {currentUserRole === 5 && (
            <button
              onClick={() => {
                resetAddForm();
                setIsAddingUser(true);
              }}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white border border-indigo-500 rounded-xl text-sm font-medium transition-colors shadow-lg shadow-indigo-500/20"
            >
              <UserPlus className="w-4 h-4" /> Add User
            </button>
          )}
          <button
            onClick={fetchUsers}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 rounded-xl text-sm font-medium transition-colors"
          >
            ↻ Refresh
          </button>
        </div>
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

      {/* Users Table */}
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
                const storeName = allStores.find((s) => s.store_id === user.store_id)?.store_name;
                const districtName = allDistricts.find((d) => d.id === user.district_id)?.district_name;
                const regionName = regions.find((r) => r.id === user.region_id)?.region_name;
                const locationText = storeName || districtName || regionName || "Unassigned";
                return (
                  <tr
                    key={user.id}
                    className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                  >
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
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium ${
                          roleColors[user.role_id] || "bg-slate-700 text-slate-300"
                        }`}
                      >
                        <ShieldCheck className="w-3 h-3" />
                        {roleLabel[user.role_id] || `Role ${user.role_id}`}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-slate-300 text-sm">{locationText}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                          user.is_active
                            ? "bg-emerald-500/10 text-emerald-400"
                            : "bg-amber-500/10 text-amber-400"
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            user.is_active ? "bg-emerald-400" : "bg-amber-400"
                          }`}
                        />
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

      {/* ── Add User Modal ── */}
      {isAddingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200 max-h-[92vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">Add New User</h3>
              <button
                onClick={() => {
                  setIsAddingUser(false);
                  resetAddForm();
                }}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Success screen */}
            {generatedPassInfo ? (
              <div className="text-center py-6">
                <div className="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h4 className="text-lg font-bold text-white mb-2">User Created!</h4>
                <p className="text-slate-400 text-sm mb-4">
                  Share this temporary password with{" "}
                  <strong className="text-white">{generatedPassInfo.name}</strong> so they can log in.
                </p>
                <div className="bg-slate-950 border border-emerald-500/30 p-4 rounded-xl mb-6">
                  <p className="text-xs text-slate-500 mb-1">Temporary Password</p>
                  <p className="text-2xl font-mono text-emerald-400 tracking-widest select-all">
                    {generatedPassInfo.pass}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setIsAddingUser(false);
                    resetAddForm();
                  }}
                  className="w-full px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-medium transition-colors"
                >
                  Done
                </button>
              </div>
            ) : (
              <>
                {addError && (
                  <div className="bg-red-500/20 border border-red-500/50 text-red-200 p-3 rounded-xl text-sm mb-5 text-center">
                    {addError}
                  </div>
                )}

                <div className="space-y-5">
                  {/* Full Name */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-slate-300">
                      Full Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={newUserName}
                      onChange={(e) => setNewUserName(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="e.g. Ravi Kumar"
                    />
                  </div>

                  {/* Email */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-slate-300">
                      Email <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="email"
                      value={newUserEmail}
                      onChange={(e) => setNewUserEmail(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="ravi@restaurant.com"
                    />
                  </div>

                  {/* Role */}
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-slate-300">
                      Role <span className="text-red-400">*</span>
                    </label>
                    <div className="relative">
                      <select
                        value={newUserRole}
                        onChange={(e) => {
                          setNewUserRole(parseInt(e.target.value));
                          setSelectedRegion("");
                          setSelectedDistrict("");
                          setSelectedStore("");
                        }}
                        className={selectCls()}
                      >
                        {ASSIGNABLE_ROLES.map((r) => (
                          <option key={r.id} value={r.id}>
                            {r.label}
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="pointer-events-none absolute right-3 top-3 w-4 h-4 text-slate-400" />
                    </div>
                    <p className="text-xs text-slate-500">
                      {newUserRole === 2 && "Requires a Region assignment."}
                      {newUserRole === 3 && "Requires Region → District assignment."}
                      {newUserRole === 4 && "Requires Region → District → Store assignment."}
                    </p>
                  </div>

                  {/* Location Assignments */}
                  <div className="border-t border-slate-800 pt-4 space-y-4">
                    <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
                      Location Assignment
                    </p>

                    {/* Region */}
                    <div className="space-y-1.5">
                      <label className="text-sm font-medium text-slate-300">
                        Region{" "}
                        {requiredFields.region && <span className="text-red-400">*</span>}
                      </label>
                      <div className="relative">
                        <select
                          value={selectedRegion}
                          onChange={(e) => {
                            setSelectedRegion(e.target.value);
                            setSelectedDistrict("");
                            setSelectedStore("");
                          }}
                          className={selectCls()}
                        >
                          <option value="">— Select Region —</option>
                          {regions.map((r) => (
                            <option key={r.id} value={r.id}>
                              {r.region_name}
                            </option>
                          ))}
                        </select>
                        <ChevronDown className="pointer-events-none absolute right-3 top-3 w-4 h-4 text-slate-400" />
                      </div>
                    </div>

                    {/* District */}
                    {requiredFields.district && (
                      <div className="space-y-1.5">
                        <label className="text-sm font-medium text-slate-300">
                          District <span className="text-red-400">*</span>
                        </label>
                          <div className="relative">
                            <select
                              value={selectedDistrict}
                              disabled={!selectedRegion}
                              onChange={(e) => {
                                setSelectedDistrict(e.target.value);
                                setSelectedStore("");
                              }}
                              className={selectCls(!selectedRegion)}
                            >
                              <option value="">
                                {selectedRegion ? "— Select District —" : "Select a region first"}
                              </option>
                              {filteredDistricts.map((d) => (
                                <option key={d.id} value={d.id}>
                                  {d.district_name}
                                </option>
                              ))}
                            </select>
                            <ChevronDown className="pointer-events-none absolute right-3 top-3 w-4 h-4 text-slate-400" />
                          </div>
                          {selectedRegion && filteredDistricts.length === 0 && (
                            <p className="text-xs text-amber-400">No districts found for this region.</p>
                          )}
                        </div>
                    )}

                    {/* Store — shown for SM (4) only */}
                    {requiredFields.store && (
                      <div className="space-y-3">
                        {!isCreatingNewStore ? (
                          <div className="space-y-1.5">
                            <label className="text-sm font-medium text-slate-300">
                              Available Stores <span className="text-red-400">*</span>
                            </label>
                            {selectedDistrict && filteredStores.length === 0 && (
                              <p className="text-sm text-amber-400 bg-amber-500/10 border border-amber-500/20 p-3 rounded-xl mb-3">
                                No available stores in this district. You can create a new store or leave this user unassigned.
                              </p>
                            )}
                            <div className="relative">
                              <select
                                value={selectedStore}
                                disabled={!selectedDistrict}
                                onChange={(e) => {
                                  const val = e.target.value;
                                  if (val === "__new__") {
                                    setIsCreatingNewStore(true);
                                    setSelectedStore("");
                                  } else {
                                    setSelectedStore(val);
                                  }
                                }}
                                className={selectCls(!selectedDistrict)}
                              >
                                <option value="">
                                  {selectedDistrict ? "— Select Available Store —" : "Select a district first"}
                                </option>
                                {filteredStores.map((s) => (
                                  <option key={s.id} value={s.id}>
                                    {s.store_name}
                                  </option>
                                ))}
                                <option value="__new__">➕ Create New Store</option>
                                <option value="unassigned">— Leave Unassigned (Empty Store User) —</option>
                              </select>
                              <ChevronDown className="pointer-events-none absolute right-3 top-3 w-4 h-4 text-slate-400" />
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-slate-300">Creating New Store</span>
                            <button
                                type="button"
                                onClick={() => {
                                  setIsCreatingNewStore(false);
                                  setSelectedStore("");
                                }}
                                className="text-xs text-indigo-400 hover:text-indigo-300"
                              >
                                Cancel
                              </button>
                          </div>
                        )}

                        {/* Inline New Store Form */}
                        {isCreatingNewStore && (
                          <div className="bg-slate-950 border border-indigo-500/30 rounded-xl p-4 space-y-3">
                            <p className="text-xs font-semibold text-indigo-400 uppercase tracking-widest">New Store Details</p>
                            <div className="space-y-1.5">
                              <label className="text-xs font-medium text-slate-400">Store Name <span className="text-red-400">*</span></label>
                              <input
                                type="text"
                                value={newStoreName}
                                onChange={(e) => setNewStoreName(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="e.g. South Store 7"
                              />
                            </div>
                            <div className="space-y-1.5">
                              <label className="text-xs font-medium text-slate-400">City</label>
                              <input
                                type="text"
                                value={newStoreCity}
                                onChange={(e) => setNewStoreCity(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="e.g. Hyderabad"
                              />
                            </div>
                            <div className="space-y-1.5">
                              <label className="text-xs font-medium text-slate-400">Address</label>
                              <input
                                type="text"
                                value={newStoreAddress}
                                onChange={(e) => setNewStoreAddress(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="e.g. Banjara Hills, Road No. 12"
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Form Actions */}
                <div className="mt-8 flex gap-3">
                  <button
                    onClick={() => {
                      setIsAddingUser(false);
                      resetAddForm();
                    }}
                    className="flex-1 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-medium transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateUser}
                    disabled={addLoading}
                    className="flex-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl font-medium shadow-lg shadow-indigo-500/20 transition-colors"
                  >
                    {addLoading ? "Creating..." : "Create User"}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ── Approval Modal ── */}
      {approvingUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-white">Approve User</h3>
              <button
                onClick={() => {
                  setApprovingUser(null);
                  setApproveRegion("");
                  setApproveDistrict("");
                  setApproveStore("");
                }}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6">
              <p className="text-sm text-slate-400 mb-2">Approving access for:</p>
              <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
                  {approvingUser.full_name?.charAt(0) || "?"}
                </div>
                <div>
                  <p className="font-medium text-white">{approvingUser.full_name}</p>
                  <p className="text-slate-400 text-xs">
                    {roleLabel[approvingUser.role_id] || `Role ${approvingUser.role_id}`}
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {/* Region */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign Region</label>
                <div className="relative">
                  <select
                    value={approveRegion}
                    onChange={(e) => {
                      setApproveRegion(e.target.value);
                      setApproveDistrict("");
                      setApproveStore("");
                    }}
                    className={selectCls()}
                  >
                    <option value="">— No Region —</option>
                    {regions.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.region_name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-3 top-3 w-4 h-4 text-slate-400" />
                </div>
              </div>
              {/* District */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign District</label>
                <div className="relative">
                  <select
                    value={approveDistrict}
                    disabled={!approveRegion}
                    onChange={(e) => {
                      setApproveDistrict(e.target.value);
                      setApproveStore("");
                    }}
                    className={selectCls(!approveRegion)}
                  >
                    <option value="">
                      {approveRegion ? "— No District —" : "Select a region first"}
                    </option>
                    {approveFilteredDistricts.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.district_name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-3 top-3 w-4 h-4 text-slate-400" />
                </div>
              </div>
              {/* Store */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-slate-300">Assign Store</label>
                <div className="relative">
                  <select
                    value={approveStore}
                    disabled={!approveDistrict}
                    onChange={(e) => setApproveStore(e.target.value)}
                    className={selectCls(!approveDistrict)}
                  >
                    <option value="">
                      {approveDistrict ? "— No Store —" : "Select a district first"}
                    </option>
                    {approveFilteredStores.map((s) => (
                      <option key={s.store_id} value={s.store_id}>
                        {s.store_name}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-3 top-3 w-4 h-4 text-slate-400" />
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-end gap-3">
              <button
                onClick={() => {
                  setApprovingUser(null);
                  setApproveRegion("");
                  setApproveDistrict("");
                  setApproveStore("");
                }}
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

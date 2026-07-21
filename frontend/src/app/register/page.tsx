"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { UserPlus, Mail, Lock, User, Briefcase } from "lucide-react";

import { getApiUrl } from "@/utils/config";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [roleId, setRoleId] = useState<number>(4); // Default: Store Manager
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [roles, setRoles] = useState<any[]>([]);

  useEffect(() => {
    // Fetch available roles
    const fetchRoles = async () => {
      try {
        const res = await fetch(getApiUrl("/roles")); 
        if (res.ok) {
          const data = await res.json();
          setRoles(data);
        } else {
           // Fallback if endpoint is protected or missing
           setRoles([
             { role_id: 2, role_name: "Regional Manager" },
             { role_id: 3, role_name: "District Manager" },
             { role_id: 4, role_name: "Store Manager" }
           ]);
        }
      } catch (e) {
          setRoles([
             { role_id: 2, role_name: "Regional Manager" },
             { role_id: 3, role_name: "District Manager" },
             { role_id: 4, role_name: "Store Manager" }
           ]);
      }
    };
    fetchRoles();
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const res = await fetch(getApiUrl("/auth/register"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          role_id: roleId,
        }),
      });

      if (!res.ok) {
        let errorMsg = "Registration failed";
        try {
          const errorData = await res.json();
          if (typeof errorData.detail === "string") {
            errorMsg = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // FastAPI validation errors come as an array
            errorMsg = errorData.detail.map((e: any) => e.msg || JSON.stringify(e)).join(", ");
          }
        } catch (err) {}
        throw new Error(errorMsg);
      }

      setSuccess("Registration successful! Your account is pending admin approval.");
      setEmail("");
      setPassword("");
      setFullName("");
      
      // Optional: Redirect to login after a few seconds
      setTimeout(() => {
          router.push("/login");
      }, 3000);
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-indigo-950 px-4">
      <div className="w-full max-w-md bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full flex items-center justify-center mx-auto shadow-lg mb-4">
            <UserPlus className="text-white w-8 h-8" />
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Request Access</h2>
          <p className="text-indigo-200 mt-2">Register for a new account</p>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-200 p-3 rounded-lg text-sm mb-6 text-center">
            {error}
          </div>
        )}
        
        {success && (
          <div className="bg-emerald-500/20 border border-emerald-500/50 text-emerald-200 p-3 rounded-lg text-sm mb-6 text-center">
            {success}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-6">
          <div className="space-y-1">
            <label className="text-sm font-medium text-indigo-100 ml-1">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-indigo-300" />
              <input
                type="text"
                required
                className="w-full bg-slate-900/50 border border-indigo-400/30 text-white rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all placeholder:text-indigo-300/50"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium text-indigo-100 ml-1">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-indigo-300" />
              <input
                type="email"
                required
                className="w-full bg-slate-900/50 border border-indigo-400/30 text-white rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all placeholder:text-indigo-300/50"
                placeholder="john@restaurant.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium text-indigo-100 ml-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-indigo-300" />
              <input
                type="password"
                required
                minLength={6}
                className="w-full bg-slate-900/50 border border-indigo-400/30 text-white rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all placeholder:text-indigo-300/50"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>
          
          <div className="space-y-1">
            <label className="text-sm font-medium text-indigo-100 ml-1">Requested Role</label>
            <div className="relative">
              <Briefcase className="absolute left-3 top-3 w-5 h-5 text-indigo-300" />
              <select
                value={roleId}
                onChange={(e) => setRoleId(parseInt(e.target.value))}
                className="w-full bg-slate-900/50 border border-indigo-400/30 text-white rounded-xl py-3 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all appearance-none"
              >
                {roles.map((r) => (
                  <option key={r.role_id} value={r.role_id} className="bg-slate-800 text-white">
                    {r.role_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={loading || !!success}
            className="w-full py-3 px-4 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white rounded-xl font-semibold shadow-lg hover:shadow-indigo-500/30 transform hover:-translate-y-0.5 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? "Submitting..." : "Submit Request"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-indigo-200">
          Already have an account?{" "}
          <a href="/login" className="text-white hover:underline font-semibold">
            Sign in
          </a>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { X, LogIn, UserPlus, Loader2 } from "lucide-react";

export default function AuthModal({ open, onClose }) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (!open) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        await register(username, password);
      }
      setUsername("");
      setPassword("");
      onClose();
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || "Something went wrong";
      setError(detail);
    } finally {
      setBusy(false);
    }
  };

  const switchMode = () => {
    setMode(mode === "login" ? "register" : "login");
    setError("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-md rounded-2xl border border-zinc-700 bg-zinc-900 p-8 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-zinc-400 hover:text-white transition-colors"
        >
          <X size={20} />
        </button>

        <div className="mb-6 text-center">
          <h2 className="text-2xl font-bold text-white">
            {mode === "login" ? "Welcome Back" : "Create Account"}
          </h2>
          <p className="mt-1 text-sm text-zinc-400">
            {mode === "login"
              ? "Sign in to access your chat history"
              : "Register to save your conversations"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-lg border border-zinc-600 bg-zinc-800 px-4 py-2.5 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Enter username"
              required
              minLength={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-zinc-600 bg-zinc-800 px-4 py-2.5 text-white placeholder-zinc-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              placeholder="Enter password"
              required
              minLength={4}
            />
          </div>

          {error && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-2 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={busy}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {busy ? (
              <Loader2 size={18} className="animate-spin" />
            ) : mode === "login" ? (
              <LogIn size={18} />
            ) : (
              <UserPlus size={18} />
            )}
            {mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-zinc-400">
          {mode === "login" ? (
            <>
              Don't have an account?{" "}
              <button onClick={switchMode} className="text-blue-400 hover:text-blue-300 transition-colors">
                Register
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button onClick={switchMode} className="text-blue-400 hover:text-blue-300 transition-colors">
                Sign In
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

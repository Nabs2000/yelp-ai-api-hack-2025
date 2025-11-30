import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Lock, Mail, LogIn, Loader2, AlertCircle } from "lucide-react";

const API_BASE_URL = "http://127.0.0.1:8000";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorMsg = "Login failed";
        try {
          const errorJson = JSON.parse(errorText);
          errorMsg = errorJson.detail || errorMsg;
        } catch {
          errorMsg =
            errorText || `Error ${response.status}: ${response.statusText}`;
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();

      console.log("Login successful:", data);
      localStorage.setItem("user", JSON.stringify(data.user));

      navigate("/dashboard");
    } catch (err: any) {
      console.error("Login Error:", err);
      if (err.message.includes("Email not confirmed")) {
        setError("Please verify your email address before logging in.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-700">
      <div className="flex justify-center mb-6">
        <div className="p-3 bg-blue-600 rounded-full">
          <LogIn className="h-8 w-8 text-white" />
        </div>
      </div>
      <h2 className="text-3xl font-bold text-center text-white mb-2">Log In</h2>
      <p className="text-center text-gray-400 mb-8">
        Sign in to access your account
      </p>

      {error && (
        <div className="mb-6 p-4 bg-red-900/50 border border-red-700 text-red-200 rounded-lg flex items-center gap-2 text-left">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-4 text-left">
          <label className="block text-gray-300 text-sm font-bold mb-2">
            Email
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-gray-500" />
            </div>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
              placeholder="you@example.com"
              required
            />
          </div>
        </div>

        <div className="mb-4 text-left">
          <label className="block text-gray-300 text-sm font-bold mb-2">
            Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock className="h-5 w-5 text-gray-500" />
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-white placeholder-gray-400"
              placeholder="••••••••"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center mt-6"
        >
          {loading ? <Loader2 className="animate-spin h-5 w-5" /> : "Sign In"}
        </button>
      </form>

      <p className="mt-6 text-center text-gray-400">
        Don't have an account?{" "}
        <Link
          to="/register"
          className="text-blue-400 hover:text-blue-300 font-semibold hover:underline"
        >
          Sign Up
        </Link>
      </p>
    </div>
  );
};

export default Login;

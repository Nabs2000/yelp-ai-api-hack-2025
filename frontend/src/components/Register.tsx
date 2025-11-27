import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, UserPlus, Loader2, AlertCircle } from 'lucide-react';

const API_BASE_URL = '[http://127.0.0.1:8000](http://127.0.0.1:8000)';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      console.log('Registration successful:', data);
      // After register, go to login
      navigate('/login');
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-700">
    <div className="flex justify-center mb-6">
        <div className="p-3 bg-green-600 rounded-full">
        <UserPlus className="h-8 w-8 text-white" />
        </div>
    </div>
    <h2 className="text-3xl font-bold text-center text-white mb-2">Create Account</h2>
    <p className="text-center text-gray-400 mb-8">Join us to get started</p>

    {error && (
        <div className="mb-6 p-4 bg-red-900/50 border border-red-700 text-red-200 rounded-lg flex items-center gap-2">
        <AlertCircle className="h-5 w-5" />
        <span>{error}</span>
        </div>
    )}

    <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 gap-4">
        <div className="mb-4 text-left">
            <label className="block text-gray-300 text-sm font-bold mb-2">First Name</label>
            <input
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-white placeholder-gray-400"
            placeholder="John"
            required
            />
        </div>
        <div className="mb-4 text-left">
            <label className="block text-gray-300 text-sm font-bold mb-2">Last Name</label>
            <input
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-white placeholder-gray-400"
            placeholder="Doe"
            required
            />
        </div>
        </div>

        <div className="mb-4 text-left">
        <label className="block text-gray-300 text-sm font-bold mb-2">Email</label>
        <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Mail className="h-5 w-5 text-gray-500" />
            </div>
            <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-white placeholder-gray-400"
            placeholder="john@example.com"
            required
            />
        </div>
        </div>

        <div className="mb-4 text-left">
        <label className="block text-gray-300 text-sm font-bold mb-2">Password</label>
        <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Lock className="h-5 w-5 text-gray-500" />
            </div>
            <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="w-full pl-10 pr-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-white placeholder-gray-400"
            placeholder="Create a strong password"
            required
            />
        </div>
        </div>

        <button
        type="submit"
        disabled={loading}
        className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center mt-6"
        >
        {loading ? <Loader2 className="animate-spin h-5 w-5" /> : 'Create Account'}
        </button>
    </form>

    <p className="mt-6 text-center text-gray-400">
        Already have an account?{' '}
        <Link to="/login" className="text-green-400 hover:text-green-300 font-semibold hover:underline">
        Sign In
        </Link>
    </p>
    </div>
  );
};

export default Register;

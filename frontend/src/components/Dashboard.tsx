import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, LogOut } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      navigate('/login');
    } else {
      setUser(JSON.parse(storedUser));
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-[#1a1a1a] p-8">
      <div className="w-full max-w-4xl mx-auto">
        <nav className="bg-gray-800 rounded-xl p-4 mb-8 flex justify-between items-center border border-gray-700 shadow-lg">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <User className="h-6 w-6 text-white" />
            </div>
            <span className="font-bold text-xl text-white">MyProject</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-gray-300 hidden sm:inline">
              Hello, {user.email}
            </span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors border border-gray-600 cursor-pointer"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </nav>

        <div className="bg-gray-800 p-8 rounded-2xl border border-gray-700 text-center shadow-xl">
          <h1 className="text-3xl font-bold text-white mb-4">Welcome to your Dashboard!</h1>
          <p className="text-gray-400">
             You are securely logged in.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

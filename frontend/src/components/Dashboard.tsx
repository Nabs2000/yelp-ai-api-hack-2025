import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, LogOut, MessageSquarePlus, MessageSquare, Loader2 } from "lucide-react";
import { type User as UserType } from "../types/user.types";
import Chatbox from "./Chatbox";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserType | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem("user");
    if (!storedUser) {
      navigate("/login");
    } else {
      setUser(JSON.parse(storedUser));
    }
  }, [navigate]);

  useEffect(() => {
    console.log("Current user:", user);
    if (user) {
      fetchConversations();
    }
  }, [user]);

  const fetchConversations = async () => {
    if (!user?.id) return;

    setIsLoadingConversations(true);
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${user.id}`);

      if (!response.ok) {
        throw new Error("Failed to fetch conversations");
      }

      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (err) {
      console.error("Error fetching conversations:", err);
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const handleNewConversation = async () => {
    if (!user?.id || isCreatingConversation) return;

    setIsCreatingConversation(true);
    try {
      const response = await fetch(`${API_BASE_URL}/start_chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: user.id }),
      });

      if (!response.ok) {
        throw new Error("Failed to start conversation");
      }

      const data = await response.json();
      setCurrentConversationId(data.conversation_id);

      // Add to conversations list
      const newConv: Conversation = {
        id: data.conversation_id,
        title: "New Moving Chat",
        created_at: new Date().toISOString(),
      };
      setConversations((prev) => [newConv, ...prev]);
    } catch (err) {
      console.error("Error creating new conversation:", err);
    } finally {
      setIsCreatingConversation(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  const handleTitleGenerated = (conversationId: string, title: string) => {
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === conversationId ? { ...conv, title } : conv
      )
    );
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-[#1a1a1a] flex">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <User className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium text-sm truncate">
                {user.user_metadata.first_name} {user.user_metadata.last_name}
              </p>
            </div>
          </div>
          <button
            onClick={handleNewConversation}
            disabled={isCreatingConversation}
            className="w-full flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isCreatingConversation ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <MessageSquarePlus className="h-4 w-4" />
            )}
            <span>New Chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {isLoadingConversations ? (
            <div className="flex items-center justify-center mt-4">
              <Loader2 className="h-6 w-6 text-gray-500 animate-spin" />
            </div>
          ) : conversations.length === 0 ? (
            <p className="text-gray-500 text-sm text-center mt-4">
              No conversations yet
            </p>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setCurrentConversationId(conv.id)}
                className={`w-full text-left p-3 rounded-lg mb-2 transition-colors cursor-pointer ${
                  currentConversationId === conv.id
                    ? "bg-gray-700 text-white"
                    : "text-gray-400 hover:bg-gray-800"
                }`}
              >
                <div className="flex items-start gap-2">
                  <MessageSquare className="h-4 w-4 mt-1 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{conv.title}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(conv.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>

        <div className="p-4 border-t border-gray-700">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors cursor-pointer"
          >
            <LogOut className="h-4 w-4" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="bg-gray-800 rounded-none border-b border-gray-700 shadow-xl flex-1 overflow-hidden flex flex-col">
          <div className="bg-gray-900 px-6 py-4 border-b border-gray-700">
            <h1 className="text-2xl font-bold text-white">
              Moving Assistant
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              Ask me anything about moving to a new city!
            </p>
          </div>
          <div className="flex-1 overflow-hidden">
            {currentConversationId ? (
              <Chatbox
                key={currentConversationId}
                conversationId={currentConversationId}
                onTitleGenerated={handleTitleGenerated}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <MessageSquare className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 text-lg mb-2">
                    Start a new conversation
                  </p>
                  <p className="text-gray-500 text-sm">
                    Click "New Chat" to begin
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

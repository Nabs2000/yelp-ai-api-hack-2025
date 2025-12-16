# Moving Assistant - AI-Powered Relocation Helper

An intelligent assistant application that helps people move from one city to another with step-by-step guidance, leveraging AI and Yelp's business data.

## Features

- **AI-Powered Chat Assistant**: Uses LangChain with GPT-3.5-turbo to provide personalized moving advice
- **Yelp Integration**: Accesses Yelp AI Chat API v2 for real-time local business recommendations
- **User Authentication**: Complete auth system with Supabase (email/password)
- **Location-Aware**: Automatically captures user location for context-aware recommendations
- **Conversation Management**: Create, view, and switch between multiple chat conversations
- **Modern UI**: Beautiful dark-themed interface with React and Tailwind CSS
- **Persistent History**: All conversations stored in Supabase for continuity

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - AI agent orchestration
- **OpenAI GPT-3.5-turbo** - Language model
- **Supabase** - Authentication & database
- **Yelp AI Chat API v2** - Business recommendations
- **UV** - Fast Python package manager

### Frontend
- **React 19** with TypeScript
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **@assistant-ui/react** - AI chat UI components
- **React Router** - Navigation
- **Lucide React** - Icons

## Project Structure

```
yelp-ai-api-hack-2025/
├── backend/
│   ├── agent/
│   │   ├── main.py         # LangChain agent setup
│   │   ├── tools.py        # Yelp AI API tool
│   │   └── prompt.py       # System prompt
│   ├── main.py             # FastAPI app & endpoints
│   ├── supabase_init.py    # Supabase client
│   ├── yelp_init.py        # Yelp v3 API (legacy)
│   └── pyproject.toml      # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Login.tsx      # Login page
    │   │   ├── Register.tsx   # Registration page
    │   │   ├── Dashboard.tsx  # Main app with sidebar
    │   │   └── Chatbox.tsx    # AI chat interface
    │   └── App.tsx            # Router setup
    └── package.json           # Node dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- UV package manager (`pip install uv`)
- Supabase account
- OpenAI API key
- Yelp API key

### Environment Setup

1. **Backend Configuration**

Create `backend/.env`:
```env
OPENAI_API_KEY=your_openai_key
YELP_API_KEY=your_yelp_key
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_anon_key
```

2. **Supabase Database Setup**

Create these tables in your Supabase project:

```sql
-- Conversations table
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  title TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT CHECK (role IN ('user', 'assistant', 'tool')),
  content TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Installation

1. **Install Backend Dependencies**
```bash
cd backend
uv sync
```

2. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

### Running the Application

1. **Start the Backend** (in `backend/` directory)
```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend will run on: `http://127.0.0.1:8000`

2. **Start the Frontend** (in `frontend/` directory)
```bash
npm run dev
```

Frontend will run on: `http://localhost:5173` (or another port if 5173 is busy)

3. **Open the App**

Navigate to the frontend URL in your browser and:
- Register a new account
- Log in
- Click "New Chat" to start a conversation
- Ask the AI assistant about moving to a new city!

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - Login with email/password

### Chat
- `POST /start_chat` - Create new conversation
  - Body: `{user_id: string}`
  - Returns: `{conversation_id: string}`

- `POST /chat` - Send message and get AI response
  - Body: `{user_id, conversation_id, message, latitude?, longitude?}`
  - Returns: `{response: string}`

## How It Works

1. **User logs in** via Supabase authentication
2. **Creates a new chat** which initializes a conversation in the database
3. **Sends a message** about moving (e.g., "I'm moving from New York to San Francisco")
4. **LangChain agent processes** the message with context about moving assistance
5. **Agent calls Yelp AI Chat API v2** if it needs local business information
6. **Receives recommendations** for movers, apartments, storage facilities, etc.
7. **Conversation history persists** in Supabase for future reference

## Features Implemented

- User registration and authentication
- Protected routes with auth validation
- Full chat UI with @assistant-ui/react
- LangChain agent with custom system prompt
- Yelp AI Chat API v2 integration
- Automatic geolocation capture
- Conversation sidebar with history
- Multiple conversation management
- Message persistence in Supabase
- Error handling and loading states
- Responsive dark-themed design

## Agent Capabilities

The AI assistant:
- Specializes in moving-related queries only
- Uses Yelp AI Chat API to find local businesses
- Provides comparisons between service providers
- Considers user's geolocation for relevant recommendations
- Maintains conversation context across messages
- Speaks with a friendly, punny personality

## Development

### Running Tests

```bash
cd backend
uv run pytest
```

### Code Structure

- **Backend**: FastAPI app with LangChain integration
- **Agent**: Custom tool for Yelp AI Chat API v2
- **Frontend**: React components with TypeScript
- **State Management**: Local state with React hooks
- **Database**: Supabase for auth, conversations, and messages

## Troubleshooting

**Backend won't start:**
- Ensure `.env` file exists with all required keys
- Check Python version is 3.11+
- Run `uv sync` to install dependencies

**Frontend won't start:**
- Run `npm install` to ensure all packages are installed
- Check Node version is 18+
- Clear node_modules and reinstall if needed

**Chat not working:**
- Verify backend is running on port 8000
- Check browser console for errors
- Ensure Supabase tables are created
- Verify OpenAI and Yelp API keys are valid

## Future Enhancements

- Stream AI responses for better UX
- Add conversation search and filtering
- Export conversations to PDF
- Implement message editing/retry
- Add file upload for moving documents
- Multi-language support
- Voice input/output
- Integration with more services (Airbnb, Zillow, etc.)

## License

MIT

## Contributors

Built during Yelp AI API Hackathon 2025

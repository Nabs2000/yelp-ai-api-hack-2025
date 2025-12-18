# Testing Checklist - Moving Assistant

This document outlines the complete testing procedure to verify all features and bug fixes.

## Prerequisites

Before testing, ensure:
- [ ] Backend `.env` file is configured with valid API keys
- [ ] Frontend `.env.local` file exists
- [ ] Supabase database tables are created
- [ ] Both backend and frontend dependencies are installed

## Starting the Application

### Backend
```bash
cd backend
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
**Expected**: Server starts on `http://127.0.0.1:8000` without errors

### Frontend
```bash
cd frontend
npm run dev
```
**Expected**: Dev server starts on `http://localhost:5173`

## Test Suite

### 1. User Registration & Authentication

#### Test 1.1: Register New User
- [ ] Navigate to `http://localhost:5173`
- [ ] Should redirect to `/login`
- [ ] Click "Sign Up" link
- [ ] Fill in registration form:
  - First Name: Test
  - Last Name: User
  - Email: test@example.com
  - Password: password123
  - Confirm Password: password123
- [ ] Click "Create Account"
- [ ] Should redirect to `/login` with success

#### Test 1.2: Login with Valid Credentials
- [ ] Enter email: test@example.com
- [ ] Enter password: password123
- [ ] Click "Sign In"
- [ ] Should redirect to `/dashboard`
- [ ] User name should appear in sidebar (Test User)

#### Test 1.3: Login Error Handling
- [ ] Logout and return to login
- [ ] Enter invalid credentials
- [ ] Should show error message in red banner
- [ ] Should not crash or redirect

### 2. Conversation Management

#### Test 2.1: Create New Conversation
- [ ] Click "New Chat" button in sidebar
- [ ] Button should show loading spinner briefly
- [ ] New conversation should appear in sidebar
- [ ] Conversation should be titled "New Moving Chat"
- [ ] Chat area should show empty chat placeholder

#### Test 2.2: Load Previous Conversations
- [ ] Refresh the browser page
- [ ] Dashboard should reload
- [ ] Previously created conversations should appear in sidebar
- [ ] Sidebar should show loading spinner while fetching
- [ ] All conversations should be ordered by most recent first

#### Test 2.3: Switch Between Conversations
- [ ] Create 2-3 new conversations
- [ ] Click on each conversation in the sidebar
- [ ] Selected conversation should highlight in sidebar
- [ ] Chat area should show "Loading conversation..." spinner
- [ ] Messages should load (empty for new conversations)

### 3. Chat Functionality

#### Test 3.1: Send First Message (Moving Request)
- [ ] Create new conversation
- [ ] Type: "I'm moving from New York to San Francisco"
- [ ] Click Send button
- [ ] User message should appear immediately in chat
- [ ] Loading spinner should appear below user message
- [ ] After 10-15 seconds, AI response should appear with:
  - Formatted markdown (headers, bullet points)
  - 7-step moving plan
  - Recommendations for movers, apartments, etc.
- [ ] Message should auto-scroll to bottom

#### Test 3.2: Send Follow-up Message
- [ ] In same conversation, type: "Tell me more about storage options"
- [ ] Click Send
- [ ] User message appears immediately
- [ ] AI responds with relevant storage information
- [ ] Response should reference previous context
- [ ] No crash or error

#### Test 3.3: Open Existing Conversation with Messages
- [ ] Create conversation and send a few messages
- [ ] Click on a different conversation in sidebar
- [ ] Click back on the conversation with messages
- [ ] Should show "Loading conversation..." spinner
- [ ] All previous messages should load in correct order
- [ ] Oldest messages at top, newest at bottom
- [ ] Can continue conversation from where left off

### 4. Error Handling

#### Test 4.1: Network Error Handling
- [ ] Stop the backend server
- [ ] Try to send a message in the chat
- [ ] Should show error message to user
- [ ] Should not crash the application
- [ ] Restart backend and verify app recovers

#### Test 4.2: Error Boundary
- [ ] Error boundary should catch any React component errors
- [ ] If error occurs, should show error page with:
  - Error message
  - "Go to Dashboard" button
- [ ] Clicking button should reset and navigate to dashboard

### 5. UI/UX Validation

#### Test 5.1: Loading States
- [ ] Creating conversation: Shows spinner in "New Chat" button
- [ ] Fetching conversations: Shows spinner in sidebar
- [ ] Loading messages: Shows spinner in chat area
- [ ] Sending message: Shows "Thinking..." indicator

#### Test 5.2: Responsive Design
- [ ] Resize browser window
- [ ] Sidebar should remain fixed width
- [ ] Chat area should expand/contract responsively
- [ ] Messages should wrap properly
- [ ] No horizontal scrolling on mobile sizes

#### Test 5.3: Markdown Rendering
- [ ] AI responses should render markdown:
  - Headers (##) as large bold text
  - Bullet points as proper lists
  - Bold/italic text formatted correctly
  - Line breaks preserved

### 6. Data Persistence

#### Test 6.1: Conversation Persistence
- [ ] Create multiple conversations
- [ ] Close browser completely
- [ ] Reopen and navigate to app
- [ ] Login again
- [ ] All conversations should still exist
- [ ] Messages should be preserved

#### Test 6.2: Message History
- [ ] Send multiple messages in a conversation
- [ ] Refresh the page
- [ ] Click on the conversation
- [ ] All messages should load in correct order
- [ ] Both user and assistant messages preserved

### 7. Logout & Session

#### Test 7.1: Logout
- [ ] Click "Logout" button in sidebar
- [ ] Should redirect to `/login`
- [ ] localStorage should be cleared
- [ ] Navigating to `/dashboard` should redirect to login

#### Test 7.2: Session Persistence
- [ ] Login to the app
- [ ] Navigate away from the site
- [ ] Return to the site
- [ ] Should still be logged in (localStorage persists)
- [ ] Dashboard should load with conversations

## API Endpoint Tests

Test these endpoints using `curl` or the Swagger docs at `http://127.0.0.1:8000/docs`:

### Authentication Endpoints
```bash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"firstName":"Test","lastName":"User","email":"test2@example.com","password":"password123"}'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test2@example.com","password":"password123"}'
```

### Conversation Endpoints
```bash
# Start chat (use user_id from login response)
curl -X POST http://127.0.0.1:8000/start_chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"YOUR_USER_ID"}'

# Get conversations
curl http://127.0.0.1:8000/conversations/YOUR_USER_ID

# Get messages for conversation
curl http://127.0.0.1:8000/conversation/CONVERSATION_ID/messages

# Send chat message
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"YOUR_USER_ID","conversation_id":"CONVERSATION_ID","message":"I need help moving"}'
```

## Performance Tests

### Expected Response Times
- [ ] User login: < 1 second
- [ ] Create conversation: < 500ms
- [ ] Fetch conversations: < 500ms
- [ ] Load messages: < 500ms
- [ ] Send message (moving request): 10-20 seconds (due to 7 Yelp API calls)
- [ ] Send follow-up: 2-5 seconds

## Known Issues to Watch For

1. **Slow Moving Requests**: Initial moving requests take 10-20 seconds due to 7 Yelp API calls
2. **Yelp Rate Limits**: May hit rate limits with frequent moving requests
3. **OpenAI API Errors**: If OpenAI key is invalid or rate limited, chat will fail

## Success Criteria

All tests should pass with:
- ✅ No console errors (check browser DevTools)
- ✅ No unhandled exceptions
- ✅ All loading states show appropriately
- ✅ Data persists correctly in Supabase
- ✅ UI remains responsive
- ✅ Error messages are user-friendly

## Bug Report Template

If you find a bug, document it with:
```
**Bug**: [Short description]
**Steps to Reproduce**:
1.
2.
3.

**Expected**: [What should happen]
**Actual**: [What actually happened]
**Console Errors**: [Any errors from browser console]
**Environment**: [Browser, OS]
```

## Completion

- [ ] All tests passed
- [ ] No critical bugs found
- [ ] Performance is acceptable
- [ ] Ready for demo/production

---

**Last Updated**: 2025-12-17
**Tested By**: [Your name]
**Test Date**: [Date]

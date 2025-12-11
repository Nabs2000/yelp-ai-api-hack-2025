from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase_init import supabase
from dotenv import load_dotenv
import json
import os
from openai import OpenAI
from yelp_init import search_yelp

load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class UserLoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str

class StartChatRequest(BaseModel):
    user_id: str

class ChatRequest(BaseModel):
    user_id: str
    conversation_id: str
    message: str

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle user authentication


@app.post("/api/auth/login")
async def login(user_login: UserLoginRequest):
    try:
        print("Logging with email:", user_login.email)
        # Sign in user
        response = supabase.auth.sign_in_with_password(
            {
                "email": user_login.email,
                "password": user_login.password,
            }
        )
        if response.user and response.session:
            return {"user": response.user.model_dump(), "session": response.session.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/auth/register")
async def register_user(register_request: RegisterRequest):
    try:
        response = supabase.auth.sign_up(
            {
                "email": register_request.email,
                "password": register_request.password,
                "options": {
                    "email_redirect_to": "http://localhost:8080/",
                    "data": {
                        "first_name": register_request.firstName,
                        "last_name": register_request.lastName,
                    }
                },
            }
        )
        print("Response:", response)
        if response.user:
            return {"user": response.user.model_dump()}
    except Exception as e:
        print("Exception:", e)
        raise HTTPException(status_code=401, detail=str(e))
    
@app.post("/start_chat")
async def start_chat_endpoint(req: StartChatRequest):
    response = supabase.table("conversations").insert({
        "user_id": req.user_id,
        "title": "New Moving Chat" 
    }).execute()
    
    new_conversation = response.data[0]
    return {"conversation_id": new_conversation["id"]}
    
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):

    history_response = supabase.table("messages")\
        .select("role, content")\
        .eq("conversation_id", req.conversation_id)\
        .order("created_at", desc=False)\
        .execute()
    
    messages = [{"role": m["role"], "content": m["content"]} for m in history_response.data]
    
    messages.append({"role": "user", "content": req.message})

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_yelp",
                "description": "Get moving services or apartment complexes in a specific location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "description": "What to search for (e.g. 'Movers', 'Apartments')"},
                        "location": {"type": "string", "description": "City and State"},
                        "price_level": {"type": "integer", "enum": [1, 2, 3, 4], "description": "Price tier 1-4"}
                    },
                    "required": ["term", "location"]
                }
            }
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = completion.choices[0].message
    final_content = response_message.content

    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]
        if tool_call.function.name == "search_yelp":
            args = json.loads(tool_call.function.arguments)
            
            yelp_data = search_yelp(args["term"], args["location"], args.get("price_level"))
            
            messages.append(response_message)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(yelp_data)
            })
            
            second_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            final_content = second_response.choices[0].message.content

    supabase.table("messages").insert([
        {"conversation_id": req.conversation_id, "role": "user", "content": req.message},
        {"conversation_id": req.conversation_id, "role": "assistant", "content": final_content}
    ]).execute()

    return {"response": final_content}

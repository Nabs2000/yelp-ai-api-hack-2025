from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase_init import supabase
from dotenv import load_dotenv
import json
import os
import requests
from openai import OpenAI

load_dotenv()

app = FastAPI()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
yelp_api_key = os.environ.get("YELP_API_KEY")


def call_yelp_ai(query: str, chat_id: str = None) -> dict:
    """Call Yelp AI Chat API v2"""
    url = "https://api.yelp.com/ai/chat/v2"
    headers = {
        "Authorization": f"Bearer {yelp_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "chat_id": chat_id if chat_id else "",
        "user_context": {}
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


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
    latitude: float | None = None
    longitude: float | None = None


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173",
                   "http://localhost:5174", "http://localhost:5175"],
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
    # Fetch conversation history from Supabase
    history_response = supabase.table("messages")\
        .select("role, content")\
        .eq("conversation_id", req.conversation_id)\
        .order("created_at", desc=False)\
        .execute()

    # Convert history to message format
    messages = [{"role": msg["role"], "content": msg["content"]}
                for msg in history_response.data]

    # Check if this is a new moving request
    moving_keywords = ["move", "moving", "relocate", "relocation"]
    is_moving_request = any(keyword in req.message.lower()
                            for keyword in moving_keywords) and len(messages) <= 1

    try:
        if is_moving_request:
            # Extract cities using GPT-4o
            city_extract_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": f"Extract the origin city and destination city from this message. Return ONLY a JSON object with 'origin' and 'destination' keys. Message: {req.message}"
                }],
                response_format={"type": "json_object"}
            )

            cities = json.loads(
                city_extract_response.choices[0].message.content)
            origin = cities.get("origin", "current location")
            destination = cities.get("destination", "new city")

            # Make multiple Yelp API calls for comprehensive information
            print(f"Making Yelp searches for move from {origin} to {destination}...")

            # Helper function to extract key info from Yelp response
            def extract_yelp_summary(yelp_response):
                try:
                    # Get just the text response from Yelp AI
                    if isinstance(yelp_response, dict) and 'response' in yelp_response:
                        return yelp_response['response'][:1000]  # Limit to 1000 chars
                    return str(yelp_response)[:1000]
                except:
                    return "No data available"

            # Make Yelp calls and extract summaries
            movers_data = call_yelp_ai(f"Find me the top 3 moving companies in {origin}")
            apartments_data = call_yelp_ai(f"Find me the top 3 apartments or housing options in {destination}")
            storage_data = call_yelp_ai(f"Find me the top 2 storage facilities in {origin} or {destination}")
            cleaning_data = call_yelp_ai(f"Find me the top 2 cleaning services in {destination}")
            furniture_data = call_yelp_ai(f"Find me the top 2 furniture stores in {destination}")
            restaurants_data = call_yelp_ai(f"Find me the top 5 restaurants in {destination}")
            activities_data = call_yelp_ai(f"Find me the top 5 fun things to do in {destination}")

            # Create a concise summary for GPT-4o
            yelp_summary = f"""
Movers in {origin}:
{extract_yelp_summary(movers_data)}

Housing in {destination}:
{extract_yelp_summary(apartments_data)}

Storage:
{extract_yelp_summary(storage_data)}

Cleaning Services in {destination}:
{extract_yelp_summary(cleaning_data)}

Furniture Stores in {destination}:
{extract_yelp_summary(furniture_data)}

Restaurants in {destination}:
{extract_yelp_summary(restaurants_data)}

Activities in {destination}:
{extract_yelp_summary(activities_data)}
"""
            
            print("Yelp summary prepared, generating moving plan...")
            print(yelp_summary)

            # Use GPT-4o to create comprehensive moving plan
            system_prompt = """You are a comprehensive moving assistant. Create a detailed, step-by-step moving plan.

Format your response in markdown with:
- Clear section headers (##)
- Bullet points for lists
- Make it comprehensive, friendly, and well-organized

Provide ALL 7 steps:
1. Professional Movers
2. Find Your New Home
3. Storage Options (if needed)
4. Set Up Utilities & Services
5. Moving Day Preparation
6. Settle Into Your New Home
7. Explore Your New City

Use the Yelp data where relevant, but also provide general advice for each step."""

            plan_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"I'm moving from {origin} to {destination}. Here's Yelp data to help:\n\n{yelp_summary}\n\nPlease create a complete 7-step moving plan."}
                ]
            )

            final_content = plan_response.choices[0].message.content

        else:
            # For follow-up questions, use regular GPT-4o chat
            messages.append({"role": "user", "content": req.message})

            chat_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful moving assistant. Answer questions about moving and relocation. Be friendly and concise."}
                ] + messages
            )

            final_content = chat_response.choices[0].message.content

        # Store both user message and assistant response in Supabase
        supabase.table("messages").insert([
            {"conversation_id": req.conversation_id,
                "role": "user", "content": req.message},
            {"conversation_id": req.conversation_id,
                "role": "assistant", "content": final_content}
        ]).execute()

        return {"response": final_content}

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()

        # Still store the user message even if there's an error
        supabase.table("messages").insert([
            {"conversation_id": req.conversation_id,
                "role": "user", "content": req.message}
        ]).execute()

        raise HTTPException(status_code=500, detail=str(e))

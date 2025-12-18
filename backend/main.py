from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase_init import supabase
from dotenv import load_dotenv
import json
import os
import requests
import httpx
import asyncio
from openai import OpenAI

load_dotenv()

app = FastAPI()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
yelp_api_key = os.environ.get("YELP_API_KEY")


def call_yelp_ai(query: str, chat_id: str = None) -> dict:
    """Call Yelp AI Chat API v2 (synchronous)"""
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


async def call_yelp_ai_async(query: str, chat_id: str = None) -> dict:
    """Call Yelp AI Chat API v2 (asynchronous)"""
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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
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


@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """Get all conversations for a user, ordered by most recent first"""
    try:
        response = supabase.table("conversations")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()

        return {"conversations": response.data}
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str):
    """Get all messages for a specific conversation, ordered chronologically"""
    try:
        response = supabase.table("messages")\
            .select("*")\
            .eq("conversation_id", conversation_id)\
            .order("created_at", desc=False)\
            .execute()

        return {"messages": response.data}
    except Exception as e:
        print(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

    # Check if this is a new moving request OR a follow-up asking for business recommendations
    moving_keywords = ["move", "moving", "relocate", "relocation"]
    is_initial_moving_request = any(keyword in req.message.lower()
                                     for keyword in moving_keywords) and len(messages) <= 1

    # Check if follow-up is asking for business recommendations
    business_keywords = ["restaurant", "food", "eat", "storage", "mover", "moving company",
                         "apartment", "housing", "hotel", "furniture", "store", "shop",
                         "cleaning", "activity", "activities", "things to do", "fun",
                         "recommend", "suggestion", "find", "looking for", "tell me about",
                         "what about", "where can i", "best", "good"]
    is_business_query = any(keyword in req.message.lower() for keyword in business_keywords)

    try:
        if is_initial_moving_request:
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
            print(
                f"Making Yelp searches for move from {origin} to {destination}...")

            # Helper function to extract key info from Yelp response
            def extract_yelp_summary(yelp_response):
                try:
                    # Get just the text response from Yelp AI
                    if isinstance(yelp_response, dict) and 'response' in yelp_response:
                        # Limit to 1000 chars
                        return yelp_response['response']['text']
                    return str(yelp_response)
                except:
                    return "No data available"

            # Make Yelp calls in parallel for better performance
            print("Making parallel Yelp API calls...")
            movers_data, apartments_data, storage_data, cleaning_data, furniture_data, restaurants_data, activities_data = await asyncio.gather(
                call_yelp_ai_async(f"Find me the top 3 moving companies in {origin}"),
                call_yelp_ai_async(f"Find me the top 3 apartments or housing options in {destination}"),
                call_yelp_ai_async(f"Find me the top 2 storage facilities in {origin} or {destination}"),
                call_yelp_ai_async(f"Find me the top 2 cleaning services in {destination}"),
                call_yelp_ai_async(f"Find me the top 2 furniture stores in {destination}"),
                call_yelp_ai_async(f"Find me the top 5 restaurants in {destination}"),
                call_yelp_ai_async(f"Find me the top 5 fun things to do in {destination}")
            )
            print("All Yelp API calls completed!")

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

        elif is_business_query and len(messages) > 0:
            # For follow-up questions asking about businesses, use Yelp
            print("Detected business query in follow-up...")

            # Use GPT to extract what they're looking for and where
            context_messages = messages[-6:] if len(messages) > 6 else messages  # Last 6 messages for context
            context_text = "\n".join([f"{m['role']}: {m['content']}" for m in context_messages])

            extract_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": f"""Based on this conversation history and current question, extract:
1. What type of business/service they're asking about
2. What city/location (use context from previous messages if not specified)

Conversation context:
{context_text}

Current question: {req.message}

Return ONLY a JSON object with 'business_type' and 'location' keys."""
                }],
                response_format={"type": "json_object"}
            )

            query_info = json.loads(extract_response.choices[0].message.content)
            business_type = query_info.get("business_type", "businesses")
            location = query_info.get("location", "the area")

            print(f"Searching Yelp for {business_type} in {location}")

            # Make targeted Yelp call (async)
            yelp_query = f"Find me the top 5 {business_type} in {location}"
            yelp_response = await call_yelp_ai_async(yelp_query)

            # Extract Yelp data
            def extract_yelp_summary(yelp_response):
                try:
                    if isinstance(yelp_response, dict) and 'response' in yelp_response:
                        return yelp_response['response']['text']
                    return str(yelp_response)
                except:
                    return "No data available"

            yelp_data = extract_yelp_summary(yelp_response)

            # Add user message to history
            messages.append({"role": "user", "content": req.message})

            # Use GPT-4o with Yelp data to answer
            chat_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful moving assistant. Answer questions about moving and relocation using the provided Yelp data when relevant. Be friendly and concise."}
                ] + messages + [
                    {"role": "system", "content": f"Here's relevant Yelp data to help answer:\n\n{yelp_data}"}
                ]
            )

            final_content = chat_response.choices[0].message.content

        else:
            # For general follow-up questions, use regular GPT-4o chat
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

        # Generate conversation title from first message
        new_title = None
        if len(messages) == 0:  # This was the first message
            try:
                title_response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": f"Generate a concise 3-6 word title for this moving conversation. Just return the title, nothing else. Message: {req.message}"
                    }],
                    max_tokens=20
                )
                new_title = title_response.choices[0].message.content.strip().strip(
                    '"').strip("'")

                # Update conversation title
                supabase.table("conversations").update({
                    "title": new_title
                }).eq("id", req.conversation_id).execute()

                print(f"Generated title: {new_title}")
            except Exception as e:
                print(f"Error generating title: {e}")
                # Continue even if title generation fails

        return {"response": final_content, "title": new_title}

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

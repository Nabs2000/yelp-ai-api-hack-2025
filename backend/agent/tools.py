import os
import requests
from pydantic import BaseModel, Field
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from langchain_core.tools import tool


load_dotenv()


@dataclass
class UserContext:
    """Class for specifying user context"""
    latitude: float
    longitude: float


class YelpQueryInput(BaseModel):
    query: str = Field(
        description="The user's query for local business information")
    chat_id: str | None = Field(
        description="Unique chat ID for maintaining conversation history", default=None)
    user_context: UserContext | None = Field(
        description="User context including geolocation", default=None)


@tool(args_schema=YelpQueryInput)
def ask_yelp(query: str, chat_id: str | None = None, user_context: UserContext | None = None) -> dict:
    """
    Calls Yelp AI API to get local business information and comparisons from a natural language query.

    Args:
    - query: The user's query for local business information.
    - chat_id: Unique chat ID for maintaining conversation history.
    - user_context: User context including locale and geolocation.

    Returns:
    - dict: JSON response from the Yelp AI API or an error message.
    """
    url = "https://api.yelp.com/ai/chat/v2"
    headers = {
        "Authorization": f"Bearer {os.getenv('YELP_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "chat_id": chat_id if chat_id else "",
        "user_context": asdict(user_context) if user_context else {}
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

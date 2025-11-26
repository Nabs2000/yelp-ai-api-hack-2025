import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class YelpQueryInput(BaseModel):
    query: str = Field(description="The user's query for local business information")
    chat_id: str | None = Field(description="Unique chat ID for maintaining conversation history", default = None)


@tool(args_schema=YelpQueryInput)
def yelp_ai_api(query: str, chat_id: str) -> dict:
    """
    Calls Yelp AI API to get local business information and comparisons from a natural language query.

    Args:
    - query: The user's query for local business information.
    - chat_id: Unique chat ID for maintaining conversation history.

    Returns:
    - dict: JSON response from the Yelp AI API or an error message.
    """
    url = "https://api.yelp.com/ai/chat/v2"
    headers = {
      "Authorization": f"Bearer {YELP_API_KEY}",
      "Content-Type": "application/json"
    }
    data = {
      "query": query,
      "chat_id": chat_id
    }

    try:
      response = requests.post(url, headers=headers, json=data)
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
      return {"error": f"API request failed: {str(e)}"}

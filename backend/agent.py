import requests
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from dataclasses import dataclass, asdict
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from prompt import SYSTEM_PROMPT
# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.agents import AgentExecutor, create_tool_calling_agent


load_dotenv()


@dataclass
class UserContext:
    """Class for specifying user context"""
    locale: str
    latitude: float
    longitude: float


class YelpQueryInput(BaseModel):
    query: str = Field(
        description="The user's query for local business information")
    chat_id: str | None = Field(
        description="Unique chat ID for maintaining conversation history", default=None)
    user_context: UserContext | None = Field(description="User context")


# @tool(args_schema=YelpQueryInput)
def yelp_ai_api(query: str, chat_id: str | None, user_context: UserContext | None) -> dict:
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


def main():
    # Test API
    model = init_chat_model("gpt-3.5-turbo")
    config: RunnableConfig = {"configurable": {"thread_id": "1"}}
    checkpointer = InMemorySaver()
    query = "I want to move to Sacramento, CA. Can you help me find moving companies there?"
    user_context = {
        "locale": "en_US",
        "latitude": 37.3387,
        "longitude": 121.8853
    }

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[yelp_ai_api],
        checkpointer=checkpointer,
        debug=True
    )
    response = agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
        config=config
    )

    print("Agent response:", response)


if __name__ == "__main__":
    main()

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
from tools import ask_yelp
# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.agents import AgentExecutor, create_tool_calling_agent


load_dotenv()


def main():
    # Test API
    model = init_chat_model("gpt-3.5-turbo")

    query = "Find me moving companies near me. I am located in San Jose, CA."

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[ask_yelp]
    )
    response = agent.invoke(
        {"messages": [{"role": "user", "content": query}]}
    )

    print("Agent response:", response)


if __name__ == "__main__":
    main()

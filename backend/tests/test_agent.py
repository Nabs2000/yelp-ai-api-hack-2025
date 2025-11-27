from agent.main import agent


class TestAgent:

    def test_failed_query(self):
        query = "What's the weather like today?"
        response = agent.invoke(
            {"messages": [{"role": "user", "content": query}]})
        ai_message_content = response["messages"][-1].content
        assert ai_message_content == "I'm sorry, but I can only assist with moving-related inquiries."

    def test_successful_query(self):
        query = "Can you help me find a moving company in San Francisco?"
        response = agent.invoke(
            {"messages": [{"role": "user", "content": query}]})
        ai_message_one = response["messages"][1]
        assert ai_message_one.tool_calls != None and ai_message_one.tool_calls[
            0]['name'] == "ask_yelp"

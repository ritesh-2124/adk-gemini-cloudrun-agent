from google.genai import Client
from .tools import summarize_tool

client = Client()


def run_agent(text: str):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
You are an AI routing agent.

Rules:
- If the user request involves summarizing text, respond ONLY with the word: CALL_SUMMARIZE_TOOL
- Do NOT summarize the text yourself
- Do NOT add any explanation

User request:
{text}
"""
    )

    result = response.text.strip()

    print("🤖 Gemini Decision:", result)

    if result == "CALL_SUMMARIZE_TOOL":
        print("⚙️ Agent decided to call summarize_tool")
        return summarize_tool(text)

    print("❌ Tool NOT used")
    return result
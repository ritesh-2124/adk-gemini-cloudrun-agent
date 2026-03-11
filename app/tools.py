from google.genai import Client

client = Client()

def summarize_tool(text: str) -> str:
    """
    Tool used by the agent to summarize text.
    """

    print("✅ TOOL EXECUTED: summarize_tool")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
Summarize the following text in exactly 20 words.

Text:
{text}
"""
    )

    return response.text
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from .tools import summarize_tool

APP_NAME = "summarizer_app"

# Define agent
agent = Agent(
    name="summarizer_agent",
    model="gemini-2.5-flash",
    description="An agent that summarizes text using the summarize_tool.",
    instruction="""You are a helpful text summarization assistant.
When a user provides text, ALWAYS use the summarize_tool first.
After the tool returns, read its output and write a SHORT, SIMPLE summary in your own words.
Rules:
- Use simple, everyday language.
- Keep it to 2-3 sentences maximum.
- Do NOT copy-paste the original text.
- Do NOT include metadata like word counts or character counts.
- Just give the summary directly, no labels or prefixes.
If the user does not provide text to summarize, politely ask them to provide some text.""",
    tools=[summarize_tool],
)

# Session storage
session_service = InMemorySessionService()

# Runner
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service,
)


async def run_agent(text: str) -> str:
    """Run the summarizer agent with the given text input."""

    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id="test-user",
    )

    content = Content(
        role="user",
        parts=[Part(text=f"Please summarize the following text:\n\n{text}")],
    )

    events = runner.run_async(
        session_id=session.id,
        new_message=content,
        user_id="test-user",
    )

    final_text = ""

    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts and event.content.parts[0].text:
                final_text = event.content.parts[0].text
            else:
                final_text = "No response from the agent."

    return final_text

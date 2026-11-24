import asyncio
import os

from dotenv import load_dotenv
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.groq import Groq

from . import tools as t
from .prompts import SYSTEM_PROMPT

load_dotenv()

TOOL_FUNCTIONS = [
    t.load_notes, t.get_notes, t.find_deadlines,
    t.add_action_item, t.list_action_items, t.mark_done, t.export_summary,
]


def build_agent() -> FunctionAgent:
    if not os.getenv("GROQ_API_KEY"):
        raise SystemExit("Set GROQ_API_KEY in your .env file first.")
    llm = Groq(model="llama-3.3-70b-versatile", api_key=os.environ["GROQ_API_KEY"], temperature=0)
    return FunctionAgent(
        tools=[FunctionTool.from_defaults(fn=f) for f in TOOL_FUNCTIONS],
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )


async def chat():
    from llama_index.core.workflow import Context

    agent = build_agent()
    ctx = Context(agent)  # keeps the conversation memory
    print("Meeting Notes Agent. Try: Analyse samples/team_meeting.md   (type 'exit' to quit)")
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        if q:
            print("Agent:", await agent.run(q, ctx=ctx))


if __name__ == "__main__":
    asyncio.run(chat())

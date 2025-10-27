import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI


load_dotenv()


async def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please add OPENAI_API_KEY to your .env file")
        return

    server_path = str(Path(__file__).parent / "server.py")

    server_params = StdioServerParameters(
        command="uv",
        args=["run", server_path],
    )

    print("🔌 Connecting to MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("🛠️  Loading tools from MCP server...")
            tools = await load_mcp_tools(session)
            print(f"✅ Loaded {len(tools)} tools: {[tool.name for tool in tools]}\n")

            model = ChatOpenAI(model="gpt-4o")
            agent = create_react_agent(model, tools)

            queries = [
                "Roll 3d6 dice for me",
                "What's an interesting fact about the number 42?",
                "Tell me a fun fact about cats",
                "Use the space_fact tool to fetch today's NASA Astronomy Picture of the Day",
            ]

            for i, query in enumerate(queries, 1):
                print("=" * 60)
                print(f"Query {i}: {query}")
                print("=" * 60)

                response = await agent.ainvoke({"messages": [("user", query)]})
                final_message = response["messages"][-1]
                print(f"\n🤖 Agent: {final_message.content}\n")


if __name__ == "__main__":
    asyncio.run(main())



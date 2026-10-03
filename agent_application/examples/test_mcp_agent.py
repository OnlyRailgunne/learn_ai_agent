import asyncio
import json
from pathlib import Path

from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from agent_application.basic_agent import available_tools
from agent_application.tool_schemas import tool_schemas


client = Groq()

MODEL = "openai/gpt-oss-120b"


def mcp_tool_to_openai_tool(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


BASE_DIR = Path(__file__).resolve().parents[2]
MCP_SERVER = BASE_DIR / "mcp_learning" / "server.py"

server_params = StdioServerParameters(
    command="python",
    args=[str(MCP_SERVER)],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # 1. 从 MCP Server 获取 Tool
            await session.initialize()

            mcp_tools = await session.list_tools()

            mcp_tool_schemas = [
                mcp_tool_to_openai_tool(tool)
                for tool in mcp_tools.tools
            ]

            # 2. 合并本地 Tool Schema + MCP Tool Schema
            tools = tool_schemas + mcp_tool_schemas

            print("=== available tools ===")

            for tool in tools:
                print(tool["function"]["name"])

            # 3. 用户输入
            messages = [
                {
                    "role": "system",
                    "content": "Use the available tools when necessary.",
                },
                {
                    "role": "user",
                    "content": "东京现在天气怎么样？",
                },
            ]

            # 4. LLM 判断是否调用 Tool
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )

            message = response.choices[0].message

            print("\n=== LLM response ===")
            print(message)

            # 5. 执行 Tool
            if message.tool_calls:

                for tool_call in message.tool_calls:

                    name = tool_call.function.name

                    arguments = json.loads(
                        tool_call.function.arguments
                    )

                    print("\n=== tool call ===")
                    print("name:", name)
                    print("arguments:", arguments)

                    # MCP Tool
                    if name in [
                        tool.name
                        for tool in mcp_tools.tools
                    ]:
                        result = await session.call_tool(
                            name,
                            arguments=arguments,
                        )

                    # Local Tool
                    elif name in available_tools:
                        result = available_tools[name](**arguments)

                    else:
                        result = f"Unknown tool: {name}"

                    print("\n=== tool result ===")
                    print(result)


if __name__ == "__main__":
    asyncio.run(main())
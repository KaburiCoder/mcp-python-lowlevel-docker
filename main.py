from ast import arguments
from typing import Annotated
from mcp import Tool
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import BaseModel, Field

# Create a server instance
server = Server("example-server")


class Fetch(BaseModel):
    """Parameters for fetching a URL."""

    chart: Annotated[str, Field(description="차트번호")]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get-birthday-by-chart",
            description="차트번호로 생년월일을 가져옵니다.",
            inputSchema=Fetch.model_json_schema(),
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "get-birthday-by-chart":
        raise ValueError(f"Unknown tool: {name}")

    args = Fetch(**arguments)

    result = {"birthday": "2000-01-01"}

    return [
        types.TextContent(
            type="text", text=f"{args.chart}의 생년월일은 {result['birthday']}입니다."
        )
    ]


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="example-prompt",
            description="An example prompt template",
            arguments=[
                types.PromptArgument(
                    name="arg1", description="Example argument", required=True
                )
            ],
        )
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    if name != "example-prompt":
        raise ValueError(f"Unknown prompt: {name}")

    return types.GetPromptResult(
        description="Example prompt",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text="Example prompt text"),
            )
        ],
    )


async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="example",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run_server():
    import asyncio

    asyncio.run(run())


if __name__ == "__main__":
    run_server()

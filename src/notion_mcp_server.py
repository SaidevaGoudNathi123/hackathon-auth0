import asyncio
import os

from dotenv import load_dotenv
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from notion_client import Client as NotionClient

from auth0_vault import get_notion_token

load_dotenv()

NOTION_DATA_SOURCE_ID = os.environ.get("NOTION_DATA_SOURCE_ID", "")

app = Server("notion-mcp-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_notion",
            description="Search Notion pages and databases by query string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_token": {
                        "type": "string",
                        "description": "Auth0 access token for this user (from OpenClaw session)",
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                },
                "required": ["user_token", "query"],
            },
        ),
        types.Tool(
            name="query_notion_data_source",
            description="Query a Notion data source (formerly database) with optional filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_token": {"type": "string"},
                    "data_source_id": {
                        "type": "string",
                        "description": "Notion data source ID (defaults to NOTION_DATA_SOURCE_ID env var)",
                    },
                    "filter": {
                        "type": "object",
                        "description": "Notion filter object (optional)",
                    },
                },
                "required": ["user_token"],
            },
        ),
        types.Tool(
            name="read_notion_page",
            description="Retrieve the content and properties of a Notion page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_token": {"type": "string"},
                    "page_id": {
                        "type": "string",
                        "description": "Notion page ID",
                    },
                },
                "required": ["user_token", "page_id"],
            },
        ),
        types.Tool(
            name="create_notion_page",
            description="Create a new page in a Notion data source.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_token": {"type": "string"},
                    "data_source_id": {"type": "string"},
                    "title": {
                        "type": "string",
                        "description": "Page title",
                    },
                    "properties": {
                        "type": "object",
                        "description": "Additional Notion properties (optional)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Optional page body text",
                    },
                },
                "required": ["user_token", "title"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    user_token = arguments["user_token"]
    notion_token = get_notion_token(user_token)
    notion = NotionClient(auth=notion_token)

    if name == "search_notion":
        results = notion.search(query=arguments["query"])
        return [types.TextContent(type="text", text=str(results))]

    elif name == "query_notion_data_source":
        ds_id = arguments.get("data_source_id") or NOTION_DATA_SOURCE_ID
        kwargs = {"data_source_id": ds_id}
        if arguments.get("filter"):
            kwargs["filter"] = arguments["filter"]
        results = notion.data_sources.query(**kwargs)
        return [types.TextContent(type="text", text=str(results))]

    elif name == "read_notion_page":
        page = notion.pages.retrieve(page_id=arguments["page_id"])
        return [types.TextContent(type="text", text=str(page))]

    elif name == "create_notion_page":
        ds_id = arguments.get("data_source_id") or NOTION_DATA_SOURCE_ID
        props = dict(arguments.get("properties") or {})
        props["title"] = {
            "title": [{"text": {"content": arguments["title"]}}]
        }
        page_args = {
            "parent": {"type": "data_source_id", "data_source_id": ds_id},
            "properties": props,
        }
        if arguments.get("content"):
            page_args["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": arguments["content"]}}
                        ]
                    },
                }
            ]
        result = notion.pages.create(**page_args)
        return [types.TextContent(type="text", text=str(result))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

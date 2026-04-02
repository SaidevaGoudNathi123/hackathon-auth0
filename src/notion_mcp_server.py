import asyncio
import os

from dotenv import load_dotenv
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from notion_client import Client as NotionClient

from auth0_vault import get_notion_token

load_dotenv()

NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")

app = Server("notion-mcp-server")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_notion",
            description="Search Notion pages by query string.",
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
            name="append_to_notion_page",
            description="Append paragraph text to an existing Notion page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_token": {"type": "string"},
                    "page_id": {
                        "type": "string",
                        "description": "Notion page ID to append content to",
                    },
                    "content": {
                        "type": "string",
                        "description": "Text content to append as a paragraph block",
                    },
                },
                "required": ["user_token", "page_id", "content"],
            },
        ),
        types.Tool(
            name="create_notion_page",
            description="Create a new Notion page as a child of an existing page.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_token": {"type": "string"},
                    "title": {
                        "type": "string",
                        "description": "Page title",
                    },
                    "parent_page_id": {
                        "type": "string",
                        "description": "Parent page ID (defaults to NOTION_PARENT_PAGE_ID env var)",
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

    elif name == "read_notion_page":
        page = notion.pages.retrieve(page_id=arguments["page_id"])
        return [types.TextContent(type="text", text=str(page))]

    elif name == "append_to_notion_page":
        result = notion.blocks.children.append(
            block_id=arguments["page_id"],
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": arguments["content"]}}
                        ]
                    },
                }
            ],
        )
        return [types.TextContent(type="text", text=str(result))]

    elif name == "create_notion_page":
        parent_id = arguments.get("parent_page_id") or NOTION_PARENT_PAGE_ID
        page_args = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "properties": {
                "title": {"title": [{"text": {"content": arguments["title"]}}]}
            },
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

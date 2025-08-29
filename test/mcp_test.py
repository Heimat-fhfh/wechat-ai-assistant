from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import TextContent
import asyncio

def get_mcp_current_date():
    async def _call():
        sse_url = "http://127.0.0.1:5002/sse"
        async with sse_client(url=sse_url) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                result = await session.call_tool("get-current-date", arguments={})
                content_item = result.content[0]
                if isinstance(content_item, TextContent):
                    return content_item.text
                else:
                    return str(content_item)
    return asyncio.run(_call())

if __name__ == "__main__":
    print(get_mcp_current_date())
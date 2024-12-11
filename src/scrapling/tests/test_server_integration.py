import asyncio
import pytest
from mcp_server_scrapling.server import ScraplingServer
from mcp.types import TextContent
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.server.stdio import stdio_server
import subprocess
import sys
import logging
import signal
from contextlib import asynccontextmanager
import threading
import os
import anyio
from anyio.streams.file import FileWriteStream, FileReadStream
from anyio.streams.buffered import BufferedByteReceiveStream
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream
from mcp.types import JSONRPCMessage, JSONRPCRequest, JSONRPCResponse, JSONRPCError
import json
import re
import queue

# Set up logging
logger = logging.getLogger("test_integration")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def log_stream(stream, prefix, log_queue=None):
    """Log lines from a stream with a prefix."""
    try:
        for line in iter(stream.readline, b''):
            decoded = line.decode().strip()
            logger.debug(f"{prefix}: {decoded}")
            if log_queue:
                log_queue.write(decoded)
    except ValueError:  # Stream closed
        pass

@asynccontextmanager
async def create_mcp_client():
    """Create and connect to an MCP client."""
    logger.info("Creating MCP client")
    
    # Create server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server_scrapling"]
    )
    
    # Create client
    async with stdio_client(server_params) as (read_stream, write_stream):
        client = ClientSession(read_stream, write_stream)
        logger.info("Client session created")
        
        # Give the client session a moment to initialize
        await asyncio.sleep(2)
        
        try:
            yield client
        finally:
            logger.info("Client session closing")

@pytest.mark.asyncio
async def test_browse_url():
    """Test browsing a URL through the scrapling server."""
    logger.info("Starting browse URL test")
    async with create_mcp_client() as client:
        # Get the list of tools
        logger.debug("Getting list of tools")
        tools = await client.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "browse"
        
        # Test browsing to a URL
        logger.debug("Calling browse tool")
        result = await client.call_tool(
            "browse",
            {
                "url": "https://example.com",
                "extract": "h1"  # try to extract the h1 element
            }
        )
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        assert len(result[0].text) > 0
        assert "Example Domain" in result[0].text  # The h1 content from example.com
        logger.info("Browse URL test completed successfully")

@pytest.mark.asyncio
async def test_invalid_url():
    """Test error handling when browsing an invalid URL."""
    logger.info("Starting invalid URL test")
    async with create_mcp_client() as client:
        logger.debug("Calling browse tool with invalid URL")
        result = await client.call_tool(
            "browse",
            {
                "url": "https://this-should-not-exist-12345.com"
            }
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error" in result[0].text
        logger.info("Invalid URL test completed successfully")

@pytest.mark.asyncio
async def test_invalid_selector():
    """Test error handling when using an invalid selector."""
    logger.info("Starting invalid selector test")
    async with create_mcp_client() as client:
        logger.debug("Calling browse tool with invalid selector")
        result = await client.call_tool(
            "browse",
            {
                "url": "https://example.com",
                "extract": "this-selector-should-not-exist-12345"
            }
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error" in result[0].text
        logger.info("Invalid selector test completed successfully")
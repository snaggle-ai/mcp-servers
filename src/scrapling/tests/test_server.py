import asyncio
import logging
from time import sleep
import pytest
from mcp_server_scrapling.server import ScraplingServer, BrowserContextManager, ChromiumOptions

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_server_initialization():
    """Test that server initialization works correctly."""
    async with BrowserContextManager(ChromiumOptions()) as cdp_url:
        logger.info(f"Browser {cdp_url}")
        
            
        server = ScraplingServer(cdp_url)
        # Server already calls _setup_handlers in __init__, so we just need to test _init_fetcher
        await server._init_fetcher()
        assert server.fetcher is not None, "Fetcher should be initialized"

        page = await server.browse_url("https://www.google.com")

        assert page is not None, "Page should be loaded"

        logger.info(f"Page: {page}")
        await asyncio.sleep(6)


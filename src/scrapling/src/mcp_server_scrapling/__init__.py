import asyncio
import logging
from mcp_server_scrapling.server import main_server

# Set up logging
logger = logging.getLogger("mcp_server_scrapling.__main__")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def main():
    logger.info("Initializing MCP Scrapling Server from __init__")
    asyncio.run(main_server())

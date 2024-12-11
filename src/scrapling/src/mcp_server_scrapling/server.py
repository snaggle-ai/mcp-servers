import asyncio
from dataclasses import dataclass, field
import logging
import os
import subprocess
import tempfile
from time import sleep
from typing import Any, Annotated, Optional

from playwright.async_api import async_playwright, Playwright
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field, AnyUrl
from mcp.server.models import InitializationOptions
from scrapling import CustomFetcher

from .PlaywrightEngine import PlaywrightEngine

# Set up detailed logging
logger = logging.getLogger("mcp_scrapling_server")

logger.info("Starting MCP Scrapling Server")

class BrowseParams(BaseModel):
    """Parameters for browsing a URL."""
    url: Annotated[AnyUrl, Field(description="URL to navigate to")]
    action: Annotated[str | None, Field(
        default=None,
        description="Custom page action to perform"
    )] = None
    wait_for: Annotated[str | None, Field(
        default=None,
        description="CSS selector to wait for"
    )] = None
    extract: Annotated[str | None, Field(
        default=None,
        description="CSS selector for content to extract"
    )] = None

class ScraplingServer():
    def __init__(self, playwright_async: Playwright):
        """Initialize the Scrapling server."""
        logger.info("Initializing ScraplingServer")
        self.fetcher: Optional[CustomFetcher] = None
        self.page = None
        self.playwright_async = playwright_async
        self._setup_handlers()
        logger.debug("ScraplingServer initialized successfully")

    async def _init_fetcher(self):
        """Initialize the PlayWrightFetcher in a separate thread."""
        logger.info("Initializing PlayWrightFetcher")
        if self.fetcher is None:
            
            try:
                logger.debug("Creating new PlayWrightFetcher instance")
                fetcher = CustomFetcher()
                logger.debug("Initializing fetcher with Google homepage")
                self.page = await fetcher.fetch("https://www.google.com", PlaywrightEngine, playwright_async=self.playwright_async, headless=False, real_chrome=True)
                self.fetcher = fetcher
                logger.info("PlayWrightFetcher initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PlayWrightFetcher: {str(e)}", exc_info=True)
                raise


    async def browse_url(self, url):
        response = await self.fetcher.fetch(url, PlaywrightEngine, playwright_async=self.playwright_async, headless=False, real_chrome=True)
        return response, PlaywrightEngine.page


    def _setup_handlers(self):
        """Set up the MCP server handlers."""
        logger.info("Setting up MCP server handlers")

@dataclass
class ChromiumOptions:
    """Options for Chromium browser."""
    headless: bool = False
    stealth: bool = True
    disable_webgl: bool = False
    hide_canvas: bool = False
    harmful_default_args: list[str] = field(default_factory=lambda: [
            # This will be ignored to avoid detection more and possibly avoid the popup crashing bug abuse: https://issues.chromium.org/issues/340836884
            '--enable-automation',
            '--disable-popup-blocking',
            '--remote-debugging-pipe',
            # '--disable-component-update',
            # '--disable-default-apps',
            # '--disable-extensions',
        ])

class BrowserContextManager:
    def __init__(self, chromium_options):
        self.chromium_options = chromium_options
        self.browser = None

    async def __aenter__(self):

        # # Prepare the flags before diving
        # flags = DEFAULT_STEALTH_FLAGS
        # if self.chromium_options.hide_canvas:
        #     flags += ['--fingerprinting-canvas-image-data-noise']
        # if self.chromium_options.disable_webgl:
        #     flags += ['--disable-webgl', '--disable-webgl-image-chromium', '--disable-webgl2']

        # port = random_port()
        # flags += [f'--remote-debugging-port={port}']
        self._playwright = async_playwright()
        self.playwright = await self._playwright.__aenter__()
        
        # self.browser = await self.playwright.chromium.launch(
        #     headless=self.chromium_options.headless, args=flags, ignore_default_args=self.chromium_options.harmful_default_args, chromium_sandbox=True, channel='chrome'
        # )

        # MacOS
        # chrome_path = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']

        # Windows
        # chrome_path = ['C:/Program Files (x86)/Google/Chrome/Application/chrome.exe']

        # Linux
        # chrome_path = ['/usr/bin/google-chrome']
        
        # port = 12345 # random_port()
        # user_data_dir = tempfile.mkdtemp()
        # args = f"--disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --no-pings --incognito --test-type --lang=en-US --mute-audio --no-first-run --disable-sync --hide-scrollbars --disable-logging --start-maximized --enable-async-dns --disable-breakpad --disable-infobars --accept-lang=en-US --use-mock-keychain --disable-translate --disable-extensions --disable-voice-input --window-position=0,0 --disable-wake-on-wifi --ignore-gpu-blocklist --enable-tcp-fast-open --enable-web-bluetooth --disable-hang-monitor --password-store=basic --disable-cloud-import --disable-default-apps --disable-print-preview --disable-dev-shm-usage --metrics-recording-only --disable-crash-reporter --disable-partial-raster --disable-gesture-typing --disable-checker-imaging --disable-prompt-on-repost --force-color-profile=srgb --font-render-hinting=none --no-default-browser-check --aggressive-cache-discard --disable-component-update --disable-cookie-encryption --disable-domain-reliability --disable-threaded-animation --disable-threaded-scrolling --enable-simple-cache-backend --disable-background-networking --disable-session-crashed-bubble --enable-surface-synchronization --disable-image-animation-resync --disable-renderer-backgrounding --disable-ipc-flooding-protection --prerender-from-omnibox=disabled --safebrowsing-disable-auto-update --disable-offer-upload-credit-cards --disable-features=site-per-process --disable-background-timer-throttling --disable-new-content-rendering-timeout --run-all-compositor-stages-before-draw --disable-client-side-phishing-detection --disable-backgrounding-occluded-windows --disable-layer-tree-host-memory-pressure --autoplay-policy=no-user-gesture-required --disable-offer-store-unmasked-wallet-cards --disable-blink-features=AutomationControlled --webrtc-ip-handling-policy=disable_non_proxied_udp --disable-component-extensions-with-background-pages --force-webrtc-ip-handling-policy=disable_non_proxied_udp --enable-features=NetworkService,NetworkServiceInProcess,TrustTokens,TrustTokensAlwaysAllowIssuance --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process,TranslateUI,BlinkGenPropertyTrees --remote-debugging-port={port} --user-data-dir={user_data_dir} --no-startup-window"
        # args = f"--disable-component-update --no-default-browser-check --disable-default-apps --no-first-run --no-service-autorun --disable-search-engine-choice-screen --mute-audio --disable-translate --disable-extensions --no-default-browser-check -remote-debugging-port={port} --user-data-dir={user_data_dir} --no-startup-window"
        # args = chrome_path + args.split(' ')
        # print(args)
        # self.browser = subprocess.run(args)
        
        await asyncio.sleep(2)
        return self.playwright

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._playwright.__aexit__(exc_type, exc_val, exc_tb)

async def main_server():
    """Run the MCP Scrapling Server."""
    logger.info("Starting browser context manager")
    try:
        chromium_options = ChromiumOptions()
        async with BrowserContextManager(chromium_options) as cdp_url:
            # logger.info(f"Browser: {browser}", dir(browser))
            serverHelper = ScraplingServer(cdp_url)
            server = Server("mcp-scrapling")

            @server.list_tools()
            async def handle_list_tools() -> list[Tool]:
                logger.debug("Handling list_tools request")
                return [
                    Tool(
                        name="browse",
                        description="Navigate to a URL and interact with the page using a real Chrome browser",
                        inputSchema=BrowseParams.model_json_schema(),
                    )
                ]

            @server.call_tool()
            async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
                logger.info(f"Handling tool call: {name} with arguments: {arguments}")
                
                if name != "browse":
                    logger.error(f"Unknown tool requested: {name}")
                    raise ValueError(f"Unknown tool: {name}")

                if not arguments:
                    logger.error("No arguments provided for tool call")
                    raise ValueError("Missing arguments")

                try:
                    params = BrowseParams(**arguments)
                    url = str(params.url)
                    logger.info(f"Processing browse request for URL: {url}")

                    # Initialize browser if needed
                    if not serverHelper.fetcher:
                        logger.debug("No fetcher instance exists, initializing new one")
                        await serverHelper._init_fetcher()

                    # Navigate to the URL
                    logger.debug(f"Navigating to URL: {url}")
                    
                    page = await serverHelper.browse_url(url or "https://www.google.com")

                    # Wait for selector if specified
                    if params.wait_for:
                        logger.debug(f"Waiting for selector: {params.wait_for}")
                        try:
                            await serverHelper._run_playwright_action(
                                page.css,
                                params.wait_for,
                                timeout=10000
                            )
                        except Exception as e:
                            logger.error(f"Failed to find selector '{params.wait_for}': {str(e)}")
                            return [TextContent(type="text", text=f"Error waiting for selector: {str(e)}")]

                    # Extract content if specified
                    if params.extract:
                        logger.debug(f"Extracting content with selector: {params.extract}")
                        try:
                            elements = await serverHelper._run_playwright_action(page.css, params.extract)
                            logger.debug(f"Found {len(elements)} elements matching selector")
                            content = []
                            for i, element in enumerate(elements):
                                text = await serverHelper._run_playwright_action(element.text)
                                if text:
                                    content.append(text.strip())
                                    logger.debug(f"Extracted text from element {i+1}: {text[:100]}...")
                            return [TextContent(type="text", text="\n".join(content))]
                        except Exception as e:
                            logger.error(f"Failed to extract content: {str(e)}")
                            return [TextContent(type="text", text=f"Error extracting content: {str(e)}")]

                    # Default to returning page title and URL
                    return [TextContent(
                        type="text",
                        text=f"Successfully loaded page URL: {url}"
                    )]

                except Exception as e:
                    logger.error(f"Error processing tool call: {str(e)}", exc_info=True)
                    return [TextContent(type="text", text=f"Error: {str(e)}")]


            logger.debug("Server instance created")

            logger.info("Starting server run")
            async with stdio_server() as (read_stream, write_stream):

                read_stream._state.max_buffer_size = 100
                write_stream._state.max_buffer_size = 100
                
                logger.info("Server running with stdio transport")
                try:
                    await server.run(
                        read_stream,
                        write_stream,
                        InitializationOptions(
                            server_name="scrapling",
                            server_version="0.1.0",
                            capabilities=server.get_capabilities(
                                notification_options=NotificationOptions(),
                                experimental_capabilities={},
                            ),
                        ),
                    )
                except Exception as e:
                    logger.error(f"Server error: {str(e)}", exc_info=True)
                    raise
        
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise

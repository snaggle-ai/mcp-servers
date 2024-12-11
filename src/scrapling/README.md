# Scrapling MCP Server

A Model Context Protocol server that provides web automation and scraping capabilities using Scrapling. This server enables LLMs to interact with web pages using a real Chrome browser, allowing for sophisticated web automation and data extraction.

## Features

- Real browser automation using Chrome
- Powerful web scraping capabilities
- Automatic handling of anti-bot protections
- Smart element tracking and content extraction

## Installation

### Prerequisites

1. Install Chrome browser on your system
2. Install `uv` from https://github.com/astral-sh/uv

### Running Locally

The simplest way to run the server is using `uvx`:

```bash
uvx --directory path/to/servers/src/scrapling run mcp-server-scrapling
```

### Configuration

Add to your Claude settings:

```json
"mcpServers": {
  "scrapling": {
    "command": "uvx",
    "args": ["--directory", "path/to/servers/src/scrapling", "run", "mcp-server-scrapling"]
  }
}
```

## Available Tools

- `browse` - Navigate to a URL and interact with the page
  - Arguments:
    - `url` (string, required): URL to navigate to
    - `action` (string, optional): Custom page action to perform
    - `wait_for` (string, optional): CSS selector to wait for
    - `extract` (string, optional): CSS selector for content to extract

## Debugging

You can use the MCP inspector to test the server:

```bash
npx @modelcontextprotocol/inspector uvx --directory path/to/servers/src/scrapling run mcp-server-scrapling
```

## License

This MCP server is licensed under the MIT License. See the LICENSE file for details. 
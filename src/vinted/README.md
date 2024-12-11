# Vinted MCP Server

This is a Model Context Protocol (MCP) server for interacting with the Vinted API. It allows AI models to search and retrieve information about listings, users, and other data from Vinted.

### Vinted API Key
[Create a Vinted API Key](https://developers.vinted.com/docs/getting-started/authentication) with appropriate permissions:
   - Go to [Vinted API Key](https://developers.vinted.com/docs/getting-started/authentication) (in Vinted Settings > Developer settings)
   - Select which repositories you'd like this token to have access to (Public, All, or Select)
   - Create a token with the `repo` scope ("Full control of private repositories")
     - Alternatively, if working only with public repositories, select only the `public_repo` scope
   - Copy the generated token

### Usage with Claude Desktop
To use this with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-vinted"],
    "env": {
      "VINTED_API_KEY": "<YOUR_API_KEY>"
    }
  }
}
```

## Installation

```bash
npm install @modelcontextprotocol/server-vinted
```

## Usage

```bash
mcp-server-vinted
```

## Configuration

The server requires the following environment variables:

- `VINTED_API_KEY` - Your Vinted API key

## Features

- Search listings
- Get listing details
- Get user profiles
- Search categories
- Get brand information

## Development

To build the server:

```bash
npm run build
```

To watch for changes during development:

```bash
npm run watch
```

## License

MIT 
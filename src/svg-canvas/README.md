# SVG Canvas MCP Server

This is a Model Context Protocol (MCP) server for creating and manipulating SVG canvases. It allows AI models to create SVG graphics programmatically by adding elements step by step.

## Installation

```bash
npm install @modelcontextprotocol/server-svg-canvas
```

## Usage

```bash
mcp-server-svg-canvas
```

## Features

- Create new SVG canvases with specified dimensions
- Add basic shapes (rect, circle, ellipse, line, polyline, polygon)
- Add path elements with SVG path commands
- Add text elements
- Style elements (fill, stroke, opacity, etc.)
- Group elements
- Apply transformations (translate, rotate, scale)
- Export SVG to string or file

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
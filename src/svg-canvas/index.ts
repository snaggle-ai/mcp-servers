#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
  CallToolResult,
} from "@modelcontextprotocol/sdk/types.js";
import path from 'path';
import { CanvasManager } from './src/canvas-manager.js';
import { CreateCanvasParams, AddElementParams } from './src/types.js';

const OUTPUT_DIR = path.join(process.cwd(), 'svg-output');

// Define the tools
const TOOLS: Tool[] = [
  {
    name: "svg_create",
    description: "Create a new SVG canvas with specified dimensions",
    inputSchema: {
      type: "object",
      properties: {
        width: { type: "number", description: "Width of the canvas in pixels" },
        height: { type: "number", description: "Height of the canvas in pixels" },
      },
      required: ["width", "height"],
    },
  },
  {
    name: "svg_add",
    description: "Add an SVG element to an existing canvas",
    inputSchema: {
      type: "object",
      properties: {
        canvasId: { type: "string", description: "ID of the canvas to modify" },
        element: {
          type: "object",
          properties: {
            type: { type: "string", enum: ["rect", "circle", "line", "text"] },
            attributes: { type: "object", additionalProperties: true },
            content: { 
              type: "string", 
              description: "Text content for text elements. Only used when type is 'text'." 
            },
          },
          required: ["type", "attributes"],
        },
      },
      required: ["canvasId", "element"],
    },
  },
  {
    name: "svg_read",
    description: "Read the SVG content of a canvas",
    inputSchema: {
      type: "object",
      properties: {
        canvasId: { type: "string", description: "ID of the canvas to read" },
        version: { type: "number", description: "Version to read (optional, defaults to latest)" },
      },
      required: ["canvasId"],
    },
  },
];

// Create canvas manager
const canvasManager = new CanvasManager(OUTPUT_DIR);

async function handleToolCall(name: string, args: any): Promise<{ toolResult: CallToolResult }> {
  switch (name) {
    case "svg_create": {
      const result = await canvasManager.createCanvas(args);
      return {
        toolResult: {
          content: [{
            type: "text",
            text: `Created canvas with ID: ${result.canvasId}\nFile: ${result.filePath}`,
          }],
          data: result,
          isError: false,
        },
      };
    }

    case "svg_add": {
      const result = await canvasManager.addElement(args);
      return {
        toolResult: {
          content: [{
            type: "text",
            text: `Added element to canvas. New version: ${result.version}\nFile: ${result.filePath}`,
          }],
          data: result,
          isError: false,
        },
      };
    }

    case "svg_read": {
      const content = await canvasManager.getSVGContent(args.canvasId, args.version);
      return {
        toolResult: {
          content: [{
            type: "text",
            text: content,
          }],
          data: { content },
          isError: false,
        },
      };
    }

    default:
      return {
        toolResult: {
          content: [{
            type: "text",
            text: `Unknown tool: ${name}`,
          }],
          isError: true,
        },
      };
  }
}

const server = new Server(
  {
    name: "svg-canvas",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {
        svg_create: {},
        svg_add: {},
        svg_read: {},
      },
    },
  },
);

// Setup request handlers
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => 
  handleToolCall(request.params.name, request.params.arguments ?? {})
);

async function runServer() {
  await canvasManager.initialize();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log('SVG Canvas MCP Server is running...');
}

runServer().catch(console.error); 

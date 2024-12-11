import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';
import os from 'os';
import { CreateCanvasParams, CreateCanvasResult, AddElementParams, AddElementResult, SVGElement } from './types.js';

export class CanvasManager {
  private outputDir: string;
  private canvasVersions: Map<string, number>;

  constructor(outputDir: string) {
    this.outputDir = outputDir;
    this.canvasVersions = new Map();
  }

  async initialize(): Promise<void> {
    this.outputDir = await fs.mkdtemp(path.join(os.tmpdir(), this.outputDir));
  }

  getAllCanvases(): Map<string, number> {
    return new Map(this.canvasVersions);
  }

  private generateCanvasId(): string {
    return crypto.randomBytes(16).toString('hex');
  }

  private getFilePath(canvasId: string, version: number): string {
    return path.join(this.outputDir, `${canvasId}_v${version}.svg`);
  }

  async getSVGContent(canvasId: string, version?: number): Promise<string> {
    const currentVersion = version ?? this.canvasVersions.get(canvasId);
    if (!currentVersion) {
      throw new Error(`Canvas not found: ${canvasId}`);
    }

    const filePath = this.getFilePath(canvasId, currentVersion);
    return await fs.readFile(filePath, 'utf-8');
  }

  async getLatestVersion(canvasId: string): Promise<number> {
    const version = this.canvasVersions.get(canvasId);
    if (!version) {
      throw new Error(`Canvas not found: ${canvasId}`);
    }
    return version;
  }

  private createSVGContent(width: number, height: number, elements: SVGElement[] = []): string {
    const elementStrings = elements.map(elem => {
      const attrs = Object.entries(elem.attributes)
        .map(([key, value]) => `${key}="${value}"`)
        .join(' ');
      
      if (elem.type === 'text' && elem.content !== undefined) {
        return `<${elem.type} ${attrs}>${elem.content}</${elem.type}>`;
      }
      
      return `<${elem.type} ${attrs}/>`;
    });

    return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
  ${elementStrings.join('\n  ')}
</svg>`;
  }

  async createCanvas(params: CreateCanvasParams): Promise<CreateCanvasResult> {
    const canvasId = this.generateCanvasId();
    const version = 1;
    this.canvasVersions.set(canvasId, version);

    const filePath = this.getFilePath(canvasId, version);
    const content = this.createSVGContent(params.width, params.height);
    
    await fs.writeFile(filePath, content, 'utf-8');

    return {
      canvasId,
      filePath,
    };
  }

  async addElement(params: AddElementParams): Promise<AddElementResult> {
    const currentVersion = this.canvasVersions.get(params.canvasId);
    if (!currentVersion) {
      throw new Error(`Canvas not found: ${params.canvasId}`);
    }

    const currentFilePath = this.getFilePath(params.canvasId, currentVersion);
    const content = await fs.readFile(currentFilePath, 'utf-8');
    
    // Parse existing SVG and extract width/height
    const widthMatch = content.match(/width="(\d+)"/);
    const heightMatch = content.match(/height="(\d+)"/);
    if (!widthMatch || !heightMatch) {
      throw new Error('Invalid SVG format');
    }

    const width = parseInt(widthMatch[1]);
    const height = parseInt(heightMatch[1]);

    // Extract existing elements
    const elementMatches = content.match(/<(rect|circle|line|text)[^>]*\/>/g) || [];
    const elements: SVGElement[] = elementMatches.map(elem => {
      const typeMatch = elem.match(/^<(\w+)/);
      const type = typeMatch?.[1] as SVGElement['type'];
      const attributes: Record<string, string | number> = {};
      
      const attrMatches = elem.matchAll(/(\w+)="([^"]*)"/g);
      for (const match of attrMatches) {
        attributes[match[1]] = match[2];
      }

      return { type, attributes };
    });

    // Add new element
    elements.push(params.element);

    // Create new version
    const newVersion = currentVersion + 1;
    this.canvasVersions.set(params.canvasId, newVersion);

    const newFilePath = this.getFilePath(params.canvasId, newVersion);
    const newContent = this.createSVGContent(width, height, elements);
    
    await fs.writeFile(newFilePath, newContent, 'utf-8');

    return {
      filePath: newFilePath,
      version: newVersion,
    };
  }
} 
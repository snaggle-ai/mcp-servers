export interface CreateCanvasParams {
  width: number;
  height: number;
}

export interface CreateCanvasResult {
  canvasId: string;
  filePath: string;
}

export interface AddElementParams {
  canvasId: string;
  element: SVGElement;
}

export interface AddElementResult {
  filePath: string;
  version: number;
}

export interface SVGElement {
  type: 'rect' | 'circle' | 'line' | 'text';
  attributes: Record<string, string | number>;
  content?: string;
} 
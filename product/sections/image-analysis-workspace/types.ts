// =============================================================================
// Data Types
// =============================================================================

export interface Image {
  id: string;
  filename: string;
  path: string;
  dimensions: { width: number; height: number };
  uploadedAt: string;
}

export interface PipelineStep {
  id: string;
  order: number;
  name: string;
  type: string;
  params: Record<string, unknown>;
}

export interface Pipeline {
  id: string;
  name: string;
  steps: PipelineStep[];
}

export interface Result {
  id: string;
  stepId: string;
  imageUrl: string;
  confluency: number | null;
  histogram?: number[];
}

export interface Annotation {
  id: string;
  type: 'point' | 'ruler' | 'rect';
  x?: number;
  y?: number;
  x1?: number;
  y1?: number;
  x2?: number;
  y2?: number;
  label?: string;
  color?: string;
  lengthPixels?: number;
}

// =============================================================================
// Component Props
// =============================================================================

export interface ImageAnalysisWorkspaceProps {
  /** The currently loaded image */
  image: Image;
  
  /** The current active pipeline */
  pipeline: Pipeline;
  
  /** Results cache for steps (keyed by stepId or list) */
  results: Result[];
  
  /** User annotations on the current image */
  annotations: Annotation[];

  /** Called when a different step is selected for viewing */
  onSelectStep?: (stepId: string) => void;

  /** Called when comparison slider moves */
  onCompare?: (stepIdA: string, stepIdB: string) => void;

  /** Called when adding a new annotation */
  onAddAnnotation?: (annotation: Annotation) => void;

  /** Called when toggling visibility of layers */
  onToggleLayer?: (layerId: string, visible: boolean) => void;
}

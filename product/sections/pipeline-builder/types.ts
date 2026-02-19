// =============================================================================
// Data Types
// =============================================================================

export interface PipelineStep {
    id: string;
    order: number;
    operationId: string;
    name: string;
    isEnabled: boolean;
    params: Record<string, unknown>;
}

export interface Pipeline {
    id: string;
    name: string;
    steps: PipelineStep[];
}

export interface AvailableOperation {
    id: string;
    name: string;
    description: string;
    defaultParams: Record<string, unknown>;
}

export interface OperationCategory {
    category: string;
    items: AvailableOperation[];
}

export interface Preset {
    id: string;
    name: string;
    description: string;
    stepCount: number;
}

// =============================================================================
// Component Props
// =============================================================================

export interface PipelineBuilderProps {
    /** The current pipeline being edited */
    pipeline: Pipeline;

    /** Catalog of available operations to add */
    availableOperations: OperationCategory[];

    /** List of saved presets */
    presets: Preset[];

    /** Called when a step is selected for editing params */
    onSelectStep?: (stepId: string) => void;

    /** Called when a step is toggled on/off */
    onToggleStep?: (stepId: string, enabled: boolean) => void;

    /** Called when steps are reordered */
    onReorderSteps?: (startIndex: number, endIndex: number) => void;

    /** Called when a new operation is added to the pipeline */
    onAddStep?: (operationId: string) => void;

    /** Called when a step is removed */
    onRemoveStep?: (stepId: string) => void;

    /** Called when pipeline params are updated */
    onUpdateParams?: (stepId: string, params: Record<string, unknown>) => void;

    /** Called when user clicks "Apply" to run the pipeline */
    onApply?: () => void;

    /** Called when user saves current pipeline as preset */
    onSavePreset?: (name: string) => void;

    /** Called when user loads a preset */
    onLoadPreset?: (presetId: string) => void;
}

// =============================================================================
// Data Types
// =============================================================================

export interface PhantastParams {
    sigma: number;
    epsilon: number;
}

export interface PhantastConfig {
    id: string;
    isEnabled: boolean;
    params: PhantastParams;
}

export interface AnalysisResult {
    confluencyPercent: number;
    processedImageUrl: string;
    maskUrl?: string;
    outlineUrl?: string;
}

export interface ViewSettings {
    showMask: boolean;
    showOutline: boolean;
    opacity?: number;
}

// =============================================================================
// Component Props
// =============================================================================

export interface PhantastIntegrationProps {
    /** The configuration for the Phantast step */
    config: PhantastConfig;

    /** The result of the analysis */
    result: AnalysisResult;

    /** Current view settings for overlays */
    viewSettings: ViewSettings;

    /** Called when parameters are updated */
    onUpdateParams?: (params: PhantastParams) => void;

    /** Called when the step is toggled on/off */
    onToggleActive?: (enabled: boolean) => void;

    /** Called when view settings are changed */
    onUpdateViewSettings?: (settings: Partial<ViewSettings>) => void;
}

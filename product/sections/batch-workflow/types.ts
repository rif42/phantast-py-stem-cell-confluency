// =============================================================================
// Data Types
// =============================================================================

export interface BatchConfig {
    addHeader: boolean;
    headerHeight: number;
    includeParameters: boolean;
    includeConfluency: boolean;
    outputFormat: 'JPG' | 'PNG' | 'TIFF';
}

export interface BatchJob {
    id: string;
    pipelineId: string;
    inputFolder: string;
    outputFolder: string;
    totalFiles: number;
}

export interface ProgressState {
    isProcessing: boolean;
    currentFileIndex: number;
    totalFiles: number;
    currentFilename: string;
    percentComplete: number;
    statusMessage: string;
}

export interface JobReport {
    jobId: string;
    completedAt: string;
    successCount: number;
    failureCount: number;
    failedFiles: string[];
}

// =============================================================================
// Component Props
// =============================================================================

export interface BatchWorkflowProps {
    /** Global settings for batch processing */
    config: BatchConfig;

    /** The currently running batch job */
    activeJob: BatchJob | null;

    /** Real-time progress update */
    progress: ProgressState | null;

    /** Completion report */
    report: JobReport | null;

    /** Called when user starts a batch job */
    onStartBatch?: (inputFolder: string, pipelineId: string) => void;

    /** Called when user cancels a running job */
    onCancelBatch?: () => void;

    /** Called when user updates output settings */
    onUpdateConfig?: (config: BatchConfig) => void;
}

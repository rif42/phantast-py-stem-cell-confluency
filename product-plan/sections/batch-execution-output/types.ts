// =============================================================================
// Data Types
// =============================================================================

export interface ProcessedStep {
    nodeName: string
    path: string
}

export interface ProcessedImage {
    originalPath: string
    steps: ProcessedStep[]
}

export interface ConfluencyResult {
    id: string
    imageName: string
    confluencyPercentage: number
    totalCellArea: number
    totalImageArea: number
    status: 'success' | 'warning' | 'error'
    errorMessage?: string
    processedImage?: ProcessedImage
}

export interface BatchJob {
    id: string
    name: string
    pipelineId: string
    inputFolder: string
    outputFolder: string
    totalImages: number
    processedImages: number
    status: 'pending' | 'running' | 'completed' | 'failed'
    startedAt: string
    completedAt?: string
}

// =============================================================================
// Component Props
// =============================================================================

export interface BatchExecutionProps {
    /** The current executing or completed batch job summary */
    batchJob: BatchJob
    /** The list of processed results to display in the data table */
    results: ConfluencyResult[]

    /** Called when user wants to start processing the selected folder */
    onRunPipeline?: () => void
    /** Called when user wants to view the deep dive processing steps for a specific image */
    onInspectResult?: (resultId: string) => void
    /** Called when user wants to open the output folder in their OS file explorer */
    onOpenOutputFolder?: () => void
    /** Called when user clicks to export the data table to a CSV file */
    onExportCsv?: () => void
}

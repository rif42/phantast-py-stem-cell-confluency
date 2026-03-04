// =============================================================================
// Data Types
// =============================================================================

export interface ConfluencyResult {
    /** the calculated confluency percentage (e.g. 82.4) */
    percentage: number
    /** total estimated cells found by the algorithm */
    totalCells: number
    /** whether the segmentation overlay mask is currently visible */
    maskVisible: boolean
}

export interface Image {
    id: string
    filename: string
    fileSize: string
    dimensions: string
    bitDepth: string
    channels: string
    format: string
    /** status represents the current processing state of the image in the workspace */
    status: 'unprocessed' | 'viewing' | 'processed' | 'error'
    /** true if this is the currently active/selected image in the main canvas */
    selected: boolean
    /** associated processing results if applicable, null if not processed */
    confluencyResult: ConfluencyResult | null
}

// =============================================================================
// Component Props
// =============================================================================

export interface ImageNavigationInspectionProps {
    /** The actively selected image to display in the main canvas */
    activeImage: Image | null

    /** The list of images in the current folder/workspace for the sidebar */
    images: Image[]

    /** Called when a user clicks an image in the folder explorer to view it */
    onSelectImage?: (id: string) => void

    /** Called when a user toggles the segmentation mask on the active image */
    onToggleMask?: (id: string, visible: boolean) => void

    /** Called when a user activates a tool (pan, zoom in, zoom out, measure, reset) from the toolbar */
    onToolSelected?: (tool: 'pan' | 'zoomIn' | 'zoomOut' | 'measure' | 'fitScreen') => void
}

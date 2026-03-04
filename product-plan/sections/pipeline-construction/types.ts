// =============================================================================
// Data Types
// =============================================================================

export interface AvailableNode {
    type: string
    name: string
    icon: string
    description: string
    helpText?: string
}

export type NodeStatus = 'active' | 'disabled' | 'error' | 'processing'

export interface ProcessNode {
    id: string
    type: string
    name: string
    description: string
    helpText?: string
    icon: string
    status: NodeStatus
    /** If false, the node is bypassed during pipeline execution */
    enabled: boolean
}

export interface Pipeline {
    id: string
    name: string
    /** The sequence of nodes from top (index 0) to bottom */
    nodes: ProcessNode[]
}

// =============================================================================
// Component Props
// =============================================================================

export interface PipelineConstructionProps {
    /** The current active pipeline structure */
    pipeline: Pipeline

    /** Catalog of node types available to add */
    availableNodes: AvailableNode[]

    /** Called when a user clicks the "Add Step" button and selects a node type */
    onAddStep?: (nodeType: string) => void

    /** Called when a user toggles the ON/OFF switch on a specific node */
    onToggleNode?: (id: string, enabled: boolean) => void

    /** Called when a user selects "Delete" from the right-click context menu */
    onDeleteNode?: (id: string) => void

    /** Called after a user drags and drops a node to reorder the stack */
    onReorderNodes?: (nodeIds: string[]) => void

    /** Called when the user clicks the main "Run Pipeline" button at the bottom */
    onRunPipeline?: () => void
}

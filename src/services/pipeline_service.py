"""Pipeline service for helper operations on pipeline nodes.

This module provides utility functions for pipeline state management
without direct model access.
"""

from typing import Any, List


class PipelineService:
    """Service for pipeline helper operations."""

    @staticmethod
    def reorder_nodes_by_id(nodes: List[Any], new_order: List[str]) -> List[Any]:
        """Reorder pipeline nodes based on a list of node IDs.

        Args:
            nodes: Current list of pipeline nodes
            new_order: List of node IDs in desired order

        Returns:
            Reordered list of nodes
        """
        id_to_node = {n.id: n for n in nodes}
        return [id_to_node[nid] for nid in new_order if nid in id_to_node]

    @staticmethod
    def has_enabled_executable_nodes(nodes: List[Any]) -> bool:
        """Return True if at least one enabled non-input node exists.

        Args:
            nodes: List of pipeline nodes

        Returns:
            True if there's at least one enabled node that's not an input node
        """
        return any(
            node.enabled
            and node.type not in {"input_single_image", "input_image_folder"}
            for node in nodes
        )

    @staticmethod
    def find_folder_node(nodes: List[Any]) -> Any:
        """Find the first folder input node in the pipeline.

        Args:
            nodes: List of pipeline nodes

        Returns:
            The folder node if found, None otherwise
        """
        for node in nodes:
            if node.type == "input_image_folder":
                return node
        return None

    @staticmethod
    def count_enabled_nodes(nodes: List[Any]) -> int:
        """Count the number of enabled nodes.

        Args:
            nodes: List of pipeline nodes

        Returns:
            Number of enabled nodes
        """
        return sum(1 for node in nodes if node.enabled)

    @staticmethod
    def get_node_types(nodes: List[Any]) -> List[str]:
        """Get list of node types.

        Args:
            nodes: List of pipeline nodes

        Returns:
            List of node type strings
        """
        return [node.type for node in nodes]

    @staticmethod
    def nodes_to_dict_list(nodes: List[Any]) -> List[dict]:
        """Convert list of PipelineNode objects to list of dicts.

        Args:
            nodes: List of PipelineNode objects

        Returns:
            List of dictionaries representing nodes
        """
        return [
            {
                "id": n.id,
                "type": n.type,
                "name": n.name,
                "description": n.description,
                "enabled": n.enabled,
                "icon": n.icon or "⚙️",
                "parameters": n.parameters,
            }
            for n in nodes
        ]

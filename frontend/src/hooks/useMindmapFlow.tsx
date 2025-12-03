import { fetchMindmap } from "@/api/article";
import type { MindTreeNode } from "@/type/mindTreeNode";
import dagre from "@dagrejs/dagre";
import { useQuery } from "@tanstack/react-query";
import type { Edge, Node } from "@xyflow/react";
import {
    Position,
    useEdgesState,
    useNodesState,
    useReactFlow
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { nanoid } from "nanoid";
import { useCallback, useEffect } from "react";

const DEFAULT_NODE_WIDTH = 180;
const DEFAULT_NODE_HEIGHT = 40;

type LayoutDirection = "LR" | "TB";

function layoutWithDagre(
  nodes: Node[],
  edges: Edge[],
  getNode: (id: string) => Node | undefined,
  direction: LayoutDirection = "LR"
): { nodes: Node[]; edges: Edge[] } {
  const dagreGraph = new dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  const isHorizontal = direction === "LR";

  dagreGraph.setGraph({ rankdir: direction });

  const getSize = (id: string) => {
    const rfNode = getNode(id);
    return {
      width: rfNode?.width ?? DEFAULT_NODE_WIDTH,
      height: rfNode?.height ?? DEFAULT_NODE_HEIGHT,
    };
  };

  nodes.forEach((node) => {
    const { width, height } = getSize(node.id);
    dagreGraph.setNode(node.id, { width, height });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const layoutedNodes = nodes.map((node) => {
    const { width, height } = getSize(node.id);
    const pos = dagreGraph.node(node.id);

    return {
      ...node,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      position: {
        x: pos.x - width / 2,
        y: pos.y - height / 2,
      },
    };
  });

  return { nodes: layoutedNodes, edges };
}

function buildFlowFromTree(root: MindTreeNode): {
  nodes: Node[];
  edges: Edge[];
} {
  const nodes: Node[] = [];
  const edges: Edge[] = [];

  const traverse = (node: MindTreeNode, parentId: string | null): string => {
    const id = nanoid();
    const hasChildren = node.children.length > 0;

    let type: "input" | "output" | "default";
    if (parentId === null) {
      type = "input";
    } else if (!hasChildren) {
      type = "output";
    } else {
      type = "default";
    }

    nodes.push({
      id,
      type,
      data: { label: node.text },
      position: { x: 0, y: 0 },
      draggable: false,
    });

    if (parentId !== null) {
      edges.push({
        id: nanoid(),
        source: parentId,
        target: id,
        animated: true,
      });
    }

    for (const child of node.children!) {
      traverse(child, id);
    }

    return id;
  };

  traverse(root, null);

  return { nodes, edges };
}

export default function useMindmapFlow(
  articleId: string,
  direction: LayoutDirection = "LR"
) {
  const { getNode } = useReactFlow();

  const [nodes, setNodes] = useNodesState<Node>([]);
  const [edges, setEdges] = useEdgesState<Edge>([]);

  const { data, isLoading, isError, error } = useQuery<MindTreeNode>({
    queryKey: ["fetch-mindmap", articleId],
    queryFn: async () => {
      const resp = await fetchMindmap({ articleId });
      return resp.data;
    },
  });
  const applyLayout = useCallback(
    (tree: MindTreeNode) => {
      const { nodes: rawNodes, edges: rawEdges } = buildFlowFromTree(tree);
      const { nodes: layoutNodes, edges: layoutEdges } = layoutWithDagre(
        rawNodes,
        rawEdges,
        getNode,
        direction
      );
      setNodes(layoutNodes);
      setEdges(layoutEdges);
    },
    [getNode, direction, setNodes, setEdges]
  );

  useEffect(() => {
    if (!data) return;
    applyLayout(data);
  }, [data, applyLayout]);

  return {
    nodes,
    edges,
    isLoading,
    isError,
    error,
  };
}

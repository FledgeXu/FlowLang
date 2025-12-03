import useMindmapFlow from "@/hooks/useMindmapFlow";
import { createFileRoute } from "@tanstack/react-router";
import { Background, ReactFlow, ReactFlowProvider } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

export const Route = createFileRoute("/mindmap")({
  component: RouteComponent,
});

function MindmapFlow() {
  const { nodes, edges } = useMindmapFlow(
    "5f9427d7-4df1-4426-88b9-dc6cf450dc03",
  );

  return (
    <ReactFlow nodes={nodes} edges={edges} nodesConnectable={false} fitView>
      <Background />
    </ReactFlow>
  );
}

function RouteComponent() {
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <ReactFlowProvider>
        <MindmapFlow />
      </ReactFlowProvider>
    </div>
  );
}

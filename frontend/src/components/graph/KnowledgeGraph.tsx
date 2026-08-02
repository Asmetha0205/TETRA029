import React, { useState, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Search, Sparkles, X } from 'lucide-react';

const initialNodes: Node[] = [
  { id: '1', position: { x: 50, y: 100 }, data: { label: 'CS106B: Programming Abstractions', type: 'course' }, className: 'p-3 rounded-2xl bg-indigo-600 text-white font-bold text-xs shadow-lg' },
  { id: '2', position: { x: 50, y: 220 }, data: { label: 'CS110: Computer Systems', type: 'course' }, className: 'p-3 rounded-2xl bg-indigo-600 text-white font-bold text-xs shadow-lg' },
  { id: '3', position: { x: 50, y: 340 }, data: { label: 'CS229: Machine Learning', type: 'course' }, className: 'p-3 rounded-2xl bg-indigo-600 text-white font-bold text-xs shadow-lg' },

  { id: '4', position: { x: 320, y: 100 }, data: { label: 'Data Structures & Algorithms', type: 'academic' }, className: 'p-3 rounded-2xl bg-emerald-600 text-white font-bold text-xs shadow-lg' },
  { id: '5', position: { x: 320, y: 220 }, data: { label: 'OS & Concurrency', type: 'academic' }, className: 'p-3 rounded-2xl bg-emerald-600 text-white font-bold text-xs shadow-lg' },
  { id: '6', position: { x: 320, y: 340 }, data: { label: 'Supervised ML Theory', type: 'academic' }, className: 'p-3 rounded-2xl bg-emerald-600 text-white font-bold text-xs shadow-lg' },

  { id: '7', position: { x: 600, y: 160 }, data: { label: 'GAP: Docker & Kubernetes', type: 'gap' }, className: 'p-3 rounded-2xl bg-rose-600 text-white font-extrabold text-xs shadow-xl animate-pulse' },
  { id: '8', position: { x: 600, y: 300 }, data: { label: 'GAP: Vector Search & RAG', type: 'gap' }, className: 'p-3 rounded-2xl bg-rose-600 text-white font-extrabold text-xs shadow-xl animate-pulse' },

  { id: '9', position: { x: 880, y: 160 }, data: { label: 'Cloud Infrastructure Architect', type: 'industry' }, className: 'p-3 rounded-2xl bg-purple-600 text-white font-bold text-xs shadow-lg' },
  { id: '10', position: { x: 880, y: 300 }, data: { label: 'AI Platform Engineer', type: 'industry' }, className: 'p-3 rounded-2xl bg-purple-600 text-white font-bold text-xs shadow-lg' },
];

const initialEdges: Edge[] = [
  { id: 'e1-4', source: '1', target: '4', animated: true },
  { id: 'e2-5', source: '2', target: '5', animated: true },
  { id: 'e3-6', source: '3', target: '6', animated: true },
  { id: 'e5-7', source: '5', target: '7', style: { stroke: '#ef4444' }, animated: true },
  { id: 'e6-8', source: '6', target: '8', style: { stroke: '#ef4444' }, animated: true },
  { id: 'e7-9', source: '7', target: '9', animated: true },
  { id: 'e8-10', source: '8', target: '10', animated: true },
];

export const KnowledgeGraph: React.FC = () => {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredNodes = useMemo(() => {
    if (!searchTerm) return nodes;
    return nodes.map((node) => {
      const labelStr = String(node.data?.label || '');
      return {
        ...node,
        hidden: !labelStr.toLowerCase().includes(searchTerm.toLowerCase()),
      };
    });
  }, [nodes, searchTerm]);

  const handleNodeClick = (_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  };

  return (
    <div className="relative w-full h-[650px] rounded-3xl border border-border/60 bg-card shadow-xl overflow-hidden flex flex-col">
      {/* Top Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 border-b border-border/50 bg-secondary/30 backdrop-blur-md z-10">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <h3 className="text-sm font-extrabold text-foreground">Neo4j Interactive Knowledge Graph</h3>
        </div>

        {/* Search Node Input */}
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search graph nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full h-8 rounded-xl border border-input bg-card pl-9 pr-3 text-xs text-foreground focus:ring-2 focus:ring-primary/40 focus:outline-none"
          />
        </div>

        {/* Legend Pills */}
        <div className="hidden lg:flex items-center space-x-3 text-[11px] font-semibold">
          <span className="flex items-center gap-1 text-indigo-500">
            <span className="h-2.5 w-2.5 rounded-full bg-indigo-600" />
            Courses
          </span>
          <span className="flex items-center gap-1 text-emerald-500">
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-600" />
            Academic Skills
          </span>
          <span className="flex items-center gap-1 text-rose-500">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-600 animate-ping" />
            Delta Skill Gaps
          </span>
          <span className="flex items-center gap-1 text-purple-500">
            <span className="h-2.5 w-2.5 rounded-full bg-purple-600" />
            Industry Job Roles
          </span>
        </div>
      </div>

      {/* React Flow Graph Area */}
      <div className="flex-1 w-full h-full relative">
        <ReactFlow
          nodes={filteredNodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleNodeClick}
          fitView
        >
          <Background color="#888" gap={20} />
          <Controls />
          <MiniMap />
        </ReactFlow>

        {/* Side Inspector Panel when Node clicked */}
        {selectedNode && (
          <div className="absolute right-4 top-4 bottom-4 w-80 bg-card/95 backdrop-blur-xl border border-border rounded-2xl p-5 shadow-2xl z-20 overflow-y-auto space-y-4 animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between border-b border-border/40 pb-3">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-primary">
                Node Inspector
              </span>
              <button
                onClick={() => setSelectedNode(null)}
                className="rounded-lg p-1 text-muted-foreground hover:bg-secondary hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div>
              <h4 className="text-base font-extrabold text-foreground">{String(selectedNode.data?.label || '')}</h4>
              <p className="text-xs text-muted-foreground capitalize">Type: {String(selectedNode.data?.type || '')}</p>
            </div>

            <div className="p-3 rounded-xl bg-secondary/40 border border-border/40 text-xs space-y-1">
              <span className="font-bold text-foreground block">Neo4j Cypher Relationship:</span>
              <p className="text-muted-foreground text-[11px]">
                (Course)-[:TEACHES]-&gt;(Skill)-[:HAS_GAP]-&gt;(IndustryRole)
              </p>
            </div>

            <button
              onClick={() => setSelectedNode(null)}
              className="w-full py-2 rounded-xl bg-secondary text-foreground text-xs font-semibold hover:bg-secondary/80"
            >
              Close Panel
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

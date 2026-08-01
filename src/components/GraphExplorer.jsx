import React, { useState, useMemo } from 'react';
import graphData from '../data/graph_sample.json';
import { Network, Zap, Shield, BookOpen, Layers, Search, Filter, RefreshCw, Info } from 'lucide-react';

export default function GraphExplorer() {
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const [activeRelation, setActiveRelation] = useState('ALL');

  // Compute node layouts dynamically in a 2D radial canvas
  const { nodes, edges } = useMemo(() => {
    const rawNodes = graphData.nodes || [];
    const rawEdges = graphData.edges || [];

    // Filter by type or relation
    const filteredNodes = rawNodes.filter(n => {
      if (selectedCategory !== 'ALL' && n.type !== selectedCategory) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return n.id.toLowerCase().includes(query) || n.label.toLowerCase().includes(query);
      }
      return true;
    });

    const activeNodeIds = new Set(filteredNodes.map(n => n.id));

    const filteredEdges = rawEdges.filter(e => {
      if (activeRelation !== 'ALL' && e.relation !== activeRelation) return false;
      return activeNodeIds.has(e.source) && activeNodeIds.has(e.target);
    });

    // Simple layout calculation: group by type in concentric circles or columns
    const width = 800;
    const height = 550;
    const centerX = width / 2;
    const centerY = height / 2;

    const emerging = filteredNodes.filter(n => n.type === 'EmergingTech');
    const roles = filteredNodes.filter(n => n.type === 'Role');
    const skills = filteredNodes.filter(n => n.type === 'Skill');
    const others = filteredNodes.filter(n => !['EmergingTech', 'Role', 'Skill'].includes(n.type));

    const layoutNodes = [];

    // EmergingTech in inner ring
    emerging.forEach((node, i) => {
      const angle = (i / Math.max(emerging.length, 1)) * 2 * Math.PI;
      const radius = 120;
      layoutNodes.push({
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        color: '#ec4899', // Pink / Rose
        bg: '#831843'
      });
    });

    // Roles in outer top
    roles.forEach((node, i) => {
      const angle = Math.PI * 1.2 + (i / Math.max(roles.length - 1, 1)) * (Math.PI * 0.6);
      const radius = 230;
      layoutNodes.push({
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        color: '#38bdf8', // Cyan
        bg: '#0c4a6e'
      });
    });

    // Skills in outer ring
    const totalOuter = skills.length + others.length;
    skills.concat(others).forEach((node, i) => {
      const angle = (i / Math.max(totalOuter, 1)) * 2 * Math.PI;
      const radius = 210;
      layoutNodes.push({
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        color: node.type === 'Skill' ? '#10b981' : '#a855f7',
        bg: node.type === 'Skill' ? '#064e3b' : '#581c87'
      });
    });

    return { nodes: layoutNodes, edges: filteredEdges };
  }, [selectedCategory, searchQuery, activeRelation]);

  const nodeMap = useMemo(() => {
    const map = new Map();
    nodes.forEach(n => map.set(n.id, n));
    return map;
  }, [nodes]);

  const selectedNode = selectedNodeId ? nodeMap.get(selectedNodeId) : null;
  const connectedEdges = selectedNodeId
    ? edges.filter(e => e.source === selectedNodeId || e.target === selectedNodeId)
    : [];

  return (
    <div className="space-y-6">
      {/* Control Header */}
      <div className="glass-panel p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-cyan-500/10 rounded-xl border border-cyan-500/20 text-cyan-400">
            <Network className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Neo4j Knowledge Graph Visualizer
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full">
                {graphData.nodes.length} Nodes &bull; {graphData.edges.length} Edges
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Interactive relationship map feeding Member 5's React Flow & Member 1's /graph endpoint
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search graph nodes..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-1.5 text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-48"
            />
          </div>

          <select
            value={selectedCategory}
            onChange={e => setSelectedCategory(e.target.value)}
            className="px-3 py-1.5 text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Node Types</option>
            <option value="EmergingTech">EmergingTech (GenAI Cluster)</option>
            <option value="Role">Role (Job Roles)</option>
            <option value="Skill">Skill (Industry Skills)</option>
          </select>

          <select
            value={activeRelation}
            onChange={e => setActiveRelation(e.target.value)}
            className="px-3 py-1.5 text-sm bg-slate-900/90 border border-slate-700/80 rounded-xl text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Relations</option>
            <option value="DEMANDS">:DEMANDS (Role → EmergingTech)</option>
            <option value="REQUIRED_BY">:REQUIRED_BY (Skill → Role)</option>
            <option value="RELATED_TO">:RELATED_TO (Skill → Skill)</option>
          </select>
        </div>
      </div>

      {/* Main Canvas + Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SVG Graph Canvas */}
        <div className="lg:col-span-3 glass-panel p-4 rounded-2xl relative border border-slate-800 overflow-hidden flex flex-col items-center justify-center min-h-[550px]">
          {/* Legend */}
          <div className="absolute top-4 left-4 flex flex-wrap gap-3 bg-slate-950/80 p-2.5 rounded-xl border border-slate-800 text-xs backdrop-blur-md z-10">
            <span className="flex items-center gap-1.5 text-rose-300">
              <span className="w-3 h-3 rounded-full bg-rose-500 inline-block shadow-sm shadow-rose-500/50"></span>
              EmergingTech (GenAI)
            </span>
            <span className="flex items-center gap-1.5 text-cyan-300">
              <span className="w-3 h-3 rounded-full bg-cyan-400 inline-block shadow-sm shadow-cyan-400/50"></span>
              Role
            </span>
            <span className="flex items-center gap-1.5 text-emerald-300">
              <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block shadow-sm shadow-emerald-500/50"></span>
              Skill
            </span>
          </div>

          <svg viewBox="0 0 800 550" className="w-full h-full max-h-[550px] cursor-grab active:cursor-grabbing">
            {/* Background Grid Lines */}
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Edges */}
            <g className="edges">
              {edges.map((edge, idx) => {
                const src = nodeMap.get(edge.source);
                const tgt = nodeMap.get(edge.target);
                if (!src || !tgt) return null;

                const isHighlighted = selectedNodeId && (edge.source === selectedNodeId || edge.target === selectedNodeId);

                let strokeColor = "rgba(148, 163, 184, 0.15)";
                if (edge.relation === 'DEMANDS') strokeColor = "rgba(236, 72, 153, 0.4)";
                if (edge.relation === 'REQUIRED_BY') strokeColor = "rgba(56, 189, 248, 0.3)";
                if (edge.relation === 'RELATED_TO') strokeColor = "rgba(16, 185, 129, 0.2)";

                if (isHighlighted) {
                  strokeColor = "#f43f5e";
                }

                return (
                  <line
                    key={`${edge.source}-${edge.target}-${edge.relation}-${idx}`}
                    x1={src.x}
                    y1={src.y}
                    x2={tgt.x}
                    y2={tgt.y}
                    stroke={strokeColor}
                    strokeWidth={isHighlighted ? 2.5 : edge.relation === 'DEMANDS' ? 1.8 : 1}
                    strokeDasharray={edge.relation === 'DEMANDS' ? '4,4' : 'none'}
                  />
                );
              })}
            </g>

            {/* Nodes */}
            <g className="nodes">
              {nodes.map(node => {
                const isSelected = selectedNodeId === node.id;
                const isEmerging = node.type === 'EmergingTech';
                const isRole = node.type === 'Role';

                const r = isEmerging ? 16 : isRole ? 18 : 12;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.x}, ${node.y})`}
                    onClick={() => setSelectedNodeId(node.id === selectedNodeId ? null : node.id)}
                    className="cursor-pointer transition-transform duration-200 hover:scale-125"
                  >
                    {/* Glow ring for selected or emerging */}
                    {(isSelected || isEmerging) && (
                      <circle
                        r={r + 6}
                        fill="none"
                        stroke={node.color}
                        strokeWidth="2"
                        opacity={isSelected ? 0.9 : 0.4}
                        className="animate-pulse"
                      />
                    )}
                    <circle
                      r={r}
                      fill={node.bg}
                      stroke={node.color}
                      strokeWidth={isSelected ? 3 : 2}
                    />
                    <text
                      y={r + 14}
                      textAnchor="middle"
                      fill="#e2e8f0"
                      fontSize={isRole || isEmerging ? "11 font-bold" : "9"}
                      className="font-medium pointer-events-none select-none drop-shadow-md"
                    >
                      {node.label.length > 18 ? node.label.substring(0, 16) + '...' : node.label}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Node Inspector Drawer */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 text-slate-400 text-xs font-semibold uppercase tracking-wider mb-4 border-b border-slate-800 pb-3">
              <Info className="w-4 h-4 text-cyan-400" />
              <span>Node Inspector</span>
            </div>

            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <span className={`inline-block px-2.5 py-1 text-xs font-bold rounded-lg mb-2 ${
                    selectedNode.type === 'EmergingTech' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                    selectedNode.type === 'Role' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' :
                    'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  }`}>
                    {selectedNode.type}
                  </span>
                  <h3 className="text-lg font-bold text-white">{selectedNode.label}</h3>
                  <code className="text-xs text-slate-400 font-mono">ID: {selectedNode.id}</code>
                </div>

                <div className="border-t border-slate-800 pt-3 space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                    Connected Edges ({connectedEdges.length})
                  </h4>
                  <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
                    {connectedEdges.map((e, idx) => {
                      const isSource = e.source === selectedNode.id;
                      const otherId = isSource ? e.target : e.source;
                      const otherNode = nodeMap.get(otherId);

                      return (
                        <div key={idx} className="p-2 bg-slate-900/80 rounded-lg text-xs border border-slate-800/80 flex items-center justify-between">
                          <span className="font-mono text-slate-400">{e.relation}</span>
                          <span className="font-semibold text-slate-200">{otherNode ? otherNode.label : otherId}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 space-y-3">
                <Network className="w-10 h-10 mx-auto stroke-1 opacity-40" />
                <p className="text-sm">Click any node in the graph to inspect relationships & properties</p>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500 font-mono">
            Shape compatible with Member 1's /graph & Member 5's React Flow
          </div>
        </div>
      </div>
    </div>
  );
}

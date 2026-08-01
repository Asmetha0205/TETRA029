import React, { useState } from 'react';
import { Terminal, Server, CheckCircle2, Copy, Download, Code, ShieldCheck } from 'lucide-react';
import graphData from '../data/graph_sample.json';

export default function AuraDBStatusCard() {
  const [copied, setCopied] = useState(false);

  const copyGraphJson = () => {
    navigator.clipboard.writeText(JSON.stringify(graphData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(graphData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "graph_sample.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-500/10 rounded-xl border border-blue-500/20 text-blue-400">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Neo4j AuraDB & Python CLI Control
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 rounded-full">
                Member 3 Driver Loaded
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Hour-zero connectivity verifier, AuraDB loader, and offline fixture generator
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Environment Credentials Setup */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            AuraDB Credentials (.env)
          </h3>
          <p className="text-xs text-slate-400">
            Copy <code className="text-cyan-300">.env.example &rarr; .env</code> in root directory. `graph_db.py` automatically reads env vars without hardcoding!
          </p>

          <pre className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-xs font-mono text-cyan-300 overflow-x-auto">
{`NEO4J_URI=neo4j+s://<instance-id>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-auradb-password>`}
          </pre>

          <div className="border-t border-slate-800 pt-4 space-y-2">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Python CLI Execution Commands
            </h4>

            <div className="space-y-2 font-mono text-xs">
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex justify-between items-center">
                <span className="text-emerald-400">python graph_db.py test</span>
                <span className="text-[10px] text-slate-500">Hour-Zero Connection Check</span>
              </div>
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex justify-between items-center">
                <span className="text-cyan-400">python graph_db.py load</span>
                <span className="text-[10px] text-slate-500">Wipe & Load AuraDB</span>
              </div>
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex justify-between items-center">
                <span className="text-purple-400">python graph_db.py graph</span>
                <span className="text-[10px] text-slate-500">Print /graph JSON</span>
              </div>
              <div className="p-2.5 bg-slate-900 rounded-lg border border-slate-800 flex justify-between items-center">
                <span className="text-amber-400">python build_graph_fixture.py</span>
                <span className="text-[10px] text-slate-500">Build Offline JSON</span>
              </div>
            </div>
          </div>
        </div>

        {/* Offline Fixture & Export */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Code className="w-4 h-4 text-purple-400" />
                Offline Graph Fixture (`graph_sample.json`)
              </h3>
              <div className="flex gap-2">
                <button
                  onClick={copyGraphJson}
                  className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 flex items-center gap-1.5 transition"
                >
                  <Copy className="w-3.5 h-3.5" />
                  {copied ? 'Copied!' : 'Copy JSON'}
                </button>
                <button
                  onClick={downloadJson}
                  className="px-3 py-1.5 text-xs bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-lg flex items-center gap-1.5 shadow-lg shadow-cyan-600/20 transition"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download
                </button>
              </div>
            </div>

            <p className="text-xs text-slate-400 mb-3">
              This exact JSON structure is served by Member 1's <code className="text-cyan-300">/graph</code> API endpoint and rendered by Member 5's React Flow component.
            </p>

            <pre className="p-4 bg-slate-900 border border-slate-800 rounded-xl text-[11px] font-mono text-emerald-400 max-h-64 overflow-y-auto">
{JSON.stringify(graphData, null, 2).substring(0, 800) + '\n... [truncated]'}
            </pre>
          </div>

          <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>51 Nodes & 201 Edges pre-computed for offline development unblocking</span>
          </div>
        </div>
      </div>
    </div>
  );
}

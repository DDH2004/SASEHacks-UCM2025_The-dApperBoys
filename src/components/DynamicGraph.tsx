import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const DynamicGraph: React.FC = () => {
  const [z, setZ] = useState<number | null>(null);
  const [x, setX] = useState<number>(0);

  const handleZChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(e.target.value);
    setZ(isNaN(value) ? null : value);
  };

  const data = useMemo(() => {
    if (z === null || x <= 0) return [];

    const points = Array.from({ length: x }, (_, i) => {
      const xi = i + 1;
      const yi = (z * Math.log(xi)) / (1000 + 100 * xi);
      return { x: xi, y: parseFloat(yi.toFixed(4)) };
    });

    return points;
  }, [z, x]);

  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow-lg border border-green-500/30 hover:shadow-green-400/40 hover:border-green-400 text-white space-y-4">
      <h2 className="text-xl font-bold text-green-400 mb-2">Dynamic Graph</h2>

      {/* Input for Z */}
      <div className="flex flex-col sm:flex-row items-center gap-4">
        <label className="text-sm text-zinc-300 font-medium">
          Enter Z:
          <input
            type="number"
            step="0.1"
            className="ml-2 px-3 py-1 rounded-md bg-zinc-800 text-white border border-zinc-600 focus:outline-none focus:ring-2 focus:ring-green-500"
            onChange={handleZChange}
            placeholder="Enter z value"
          />
        </label>

        {/* Slider */}
        <div className="flex-1">
          <label className="text-sm text-zinc-300">
            Adjust X (days): {x}
            <input
              type="range"
              min={1}
              max={100}
              value={x}
              onChange={(e) => setX(parseInt(e.target.value))}
              disabled={z === null}
              className="w-full mt-2 accent-green-500 cursor-pointer disabled:opacity-40"
            />
          </label>
        </div>
      </div>

      {/* Graph */}
      <div className="h-72 bg-zinc-800 rounded-lg border border-zinc-700 p-4">
        {z === null ? (
          <p className="text-center text-zinc-400 italic mt-20">
            Enter a value for Z to activate the graph
          </p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="x" stroke="#aaa" />
              <YAxis stroke="#aaa" />
              <Tooltip />
              <Line type="monotone" dataKey="y" stroke="#22C55E" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};

export default DynamicGraph;

import React, { useState, useEffect } from 'react';
import { ShieldCheck, Calendar, Users } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function TrustedDashboard({ verifiedData }) {
  // 1. State to hold the historical data from our SQLite database
  const [dbStats, setDbStats] = useState([]);

  // 2. Fetch the aggregated data from the backend on load
  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/dashboard-stats")
      .then(res => res.json())
      .then(data => setDbStats(data))
      .catch(err => console.error("Error fetching stats:", err));
  }, []);

  if (!verifiedData || verifiedData.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-80px)] text-gray-400">
        <ShieldCheck size={64} className="mb-4 text-gray-300" />
        <h2 className="text-xl font-bold">No Verified Records Yet</h2>
        <p className="text-sm">Process and verify a judgment in the Cockpit first.</p>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 min-h-[calc(100vh-80px)]">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">Department War Room</h1>
          <p className="text-gray-500">Showing verified, actionable directives across all cases.</p>
        </header>

        {/* KPI Cards (Current Session) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-gray-500 font-semibold mb-2">Total Verified Actions</h3>
            <div className="text-4xl font-bold text-blue-600">{verifiedData.reduce((acc, curr) => acc + curr.directions.length, 0)}</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-gray-500 font-semibold mb-2">Pending Appeals</h3>
            <div className="text-4xl font-bold text-red-500">
               {verifiedData.flatMap(d => d.directions).filter(d => d.compliance_vs_appeal === 'APPEAL').length}
            </div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
             <h3 className="text-gray-500 font-semibold mb-2">To Comply</h3>
            <div className="text-4xl font-bold text-green-500">
               {verifiedData.flatMap(d => d.directions).filter(d => d.compliance_vs_appeal === 'COMPLY').length}
            </div>
          </div>
        </div>

        {/* NEW: Recharts Database Visualization */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 h-96">
          <h3 className="text-gray-800 font-bold mb-4">Historical Department Posture (Database)</h3>
          {dbStats.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dbStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="COMPLY" stackId="a" fill="#10B981" name="Compliance Required" />
                <Bar dataKey="APPEAL" stackId="a" fill="#EF4444" name="Appeal Recommended" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
             <div className="flex items-center justify-center h-full text-gray-400">
                Send data from the Review Cockpit to populate this chart!
             </div>
          )}
        </div>

        {/* Raw Data Table (Current Session) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100 text-gray-600 text-sm uppercase tracking-wider">
                <th className="p-4 border-b">Case Title</th>
                <th className="p-4 border-b">Department / Subject</th>
                <th className="p-4 border-b">Action Required</th>
                <th className="p-4 border-b">Strategy</th>
                <th className="p-4 border-b">Timeline</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {verifiedData.flatMap((caseData, caseIdx) => 
                caseData.directions.map((dir, dirIdx) => (
                  <tr key={`${caseIdx}-${dirIdx}`} className="border-b hover:bg-gray-50 transition-colors">
                    <td className="p-4 font-medium text-slate-800">{caseData.case_metadata?.case_title || "Unknown Case"}</td>
                    <td className="p-4"><div className="flex items-center gap-2"><Users size={16} className="text-gray-400"/> {dir.action_subject}</div></td>
                    <td className="p-4 text-gray-600">{dir.action_verb}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${dir.compliance_vs_appeal === 'APPEAL' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                        {dir.compliance_vs_appeal}
                      </span>
                    </td>
                    <td className="p-4"><div className="flex items-center gap-2"><Calendar size={16} className="text-gray-400"/> {dir.timeline_explicit || dir.timeline_inferred || "None"}</div></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Activity, ShieldCheck } from 'lucide-react';
import VerificationCockpit from './components/VerificationCockpit';
import TrustedDashboard from './components/TrustedDashboard';

export default function App() {
  const [file, setFile] = useState(null);
  const [appData, setAppData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('cockpit'); // 'cockpit' or 'dashboard'
  const [verifiedRecords, setVerifiedRecords] = useState([]);

  const processFile = async () => {
    if (!file) return alert("Please select a PDF first.");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post("http://localhost:8000/api/process-judgment", formData);
      if(res.data.status === "error") throw new Error(res.data.message);
      setAppData(res.data);
      setActiveTab('cockpit');
    } catch (err) {
      console.error(err);
      alert("Extraction failed: " + (err.message || "Ensure backend is running and API key is set."));
    }
    setLoading(false);
  };

  const handleVerifyAll = (verifiedGenome) => {
    setVerifiedRecords([...verifiedRecords, verifiedGenome]);
    setAppData(null); // Clear cockpit
    setFile(null); // Clear file input
    setActiveTab('dashboard'); // Switch to dashboard
  };

  return (
    <div className="min-h-screen flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="bg-slate-900 text-white h-20 px-6 flex justify-between items-center z-10 shadow-md shrink-0">
        <div className="flex items-center gap-8">
          <h1 className="font-bold text-2xl tracking-wide bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">CCMS Legal DNA</h1>
          <nav className="flex gap-4">
            <button onClick={() => setActiveTab('cockpit')} className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'cockpit' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'}`}>
              <Activity size={18}/> Review Cockpit
            </button>
            <button onClick={() => setActiveTab('dashboard')} className={`flex items-center gap-2 px-3 py-2 rounded-md transition-colors ${activeTab === 'dashboard' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'}`}>
              <ShieldCheck size={18}/> Trusted Dashboard
              {verifiedRecords.length > 0 && <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">{verifiedRecords.length}</span>}
            </button>
          </nav>
        </div>
        
        <div className="flex items-center gap-4 bg-slate-800 p-2 rounded-lg border border-slate-700">
          <input type="file" accept=".pdf" onChange={e => setFile(e.target.files[0])} className="text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700" />
          <button onClick={processFile} disabled={loading} className="bg-indigo-600 px-6 py-2 rounded-md text-sm font-semibold hover:bg-indigo-500 transition disabled:opacity-50 flex items-center gap-2">
            {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div> : <Upload size={18}/>}
            {loading ? "Mapping DNA..." : "Process Judgment"}
          </button>
        </div>
      </header>
      
      {/* Main Content Area */}
      <main className="flex-1 bg-gray-100">
        {activeTab === 'cockpit' && !appData && !loading && (
          <div className="flex flex-col items-center justify-center h-[calc(100vh-80px)] text-gray-400">
            <Upload size={64} className="mb-4 text-gray-300" />
            <h2 className="text-xl font-bold text-gray-500">Awaiting High Court Judgment</h2>
            <p className="text-sm mt-2">Upload a PDF in the top right to generate the Legal DNA and begin verification.</p>
          </div>
        )}
        
        {activeTab === 'cockpit' && loading && (
          <div className="flex flex-col items-center justify-center h-[calc(100vh-80px)]">
             <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mb-6"></div>
             <p className="text-lg font-semibold text-gray-600 animate-pulse">Running Layer 1: Semantic Zoning...</p>
          </div>
        )}

        {activeTab === 'cockpit' && appData && (
          <VerificationCockpit data={appData} rawTextBlocks={appData.zoned_text} onVerifyAll={handleVerifyAll} />
        )}

        {activeTab === 'dashboard' && (
          <TrustedDashboard verifiedData={verifiedRecords} />
        )}
      </main>
    </div>
  );
}
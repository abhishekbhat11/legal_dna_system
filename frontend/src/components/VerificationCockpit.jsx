import React, { useState } from 'react';
import { Check, AlertTriangle, ArrowRight } from 'lucide-react';

export default function VerificationCockpit({ data, rawTextBlocks, onVerifyAll }) {
  const [genome, setGenome] = useState(data.genome);
  const [verifiedFields, setVerifiedFields] = useState({});

  const toggleApproval = (directionIdx, field) => {
    const key = `${directionIdx}-${field}`;
    setVerifiedFields(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // NEW: The Delivery Truck function that loops through all cards and saves them
  const handleSendToDashboard = async () => {
    try {
      // Loop through every direction and send it to the SQLite database
      for (const direction of genome.directions) {
        await fetch("http://127.0.0.1:8000/api/save-dna", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action_subject: direction.action_subject,
            action_verb: direction.action_verb,
            timeline: direction.timeline_explicit || direction.timeline_inferred || "None",
            strategy: direction.compliance_vs_appeal,
            source_text: direction.source_span?.exact_text || "No source text provided."
          }),
        });
      }

      alert("Success! All directives saved to Mission Control Dashboard.");
      
      // Also trigger your original onVerifyAll function so the rest of your app updates
      if (onVerifyAll) {
        onVerifyAll(genome);
      }
    } catch (error) {
      console.error("Error saving data:", error);
      alert("Could not connect to the backend to save data.");
    }
  };

  return (
    <div className="flex h-[calc(100vh-80px)] bg-gray-50 overflow-hidden">
      {/* LEFT PANEL: Document Viewer */}
      <div className="w-1/2 bg-white border-r border-gray-300 overflow-y-auto p-8 shadow-inner">
        <h2 className="text-xl font-bold mb-6 border-b pb-2 text-slate-800">Source Document Zones</h2>
        <div className="text-sm leading-relaxed font-serif text-gray-800 space-y-4">
          {rawTextBlocks.map((block, idx) => (
            <p key={idx} className={`p-3 rounded-md transition-colors ${
              block.zone === 'Direction Zone' ? 'bg-yellow-50 border-l-4 border-yellow-400' :
              block.zone === 'Observation Zone' ? 'bg-blue-50 border-l-4 border-blue-400' : 
              block.zone === 'Preamble Zone' ? 'bg-gray-100' : ''
            }`}>
              <span className="text-[10px] font-sans font-bold text-gray-400 uppercase tracking-wider block mb-1">
                [{block.zone}] (Chars: {block.start_char}-{block.end_char})
              </span>
              {block.text}
            </p>
          ))}
        </div>
      </div>

      {/* RIGHT PANEL: Legal DNA Cockpit */}
      <div className="w-1/2 overflow-y-auto p-6 bg-slate-50">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-slate-800">Verification Cockpit</h2>
          <button 
            // NEW: Hooked up the button to our new save function!
            onClick={handleSendToDashboard}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-semibold flex items-center gap-2 transition-colors">
            Send to Dashboard <ArrowRight size={16}/>
          </button>
        </div>
        
        {genome.directions.map((dir, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 mb-6 overflow-hidden">
            <div className="bg-slate-800 text-white px-4 py-3 flex justify-between items-center">
              <span className="font-semibold tracking-wide">Direction {idx + 1}</span>
              <div className="flex gap-4 text-xs font-mono">
                 <span title="Extraction Confidence" className="text-blue-300">Ext: {dir.confidence.extraction_confidence}%</span>
                 <span title="Timeline Confidence" className="text-yellow-300">Time: {dir.confidence.timeline_confidence}%</span>
              </div>
            </div>

            <div className="p-5 space-y-4">
              {/* Micro-Approvals */}
              {[
                { label: "Action Subject", value: dir.action_subject, key: "subject" },
                { label: "Action Verb", value: dir.action_verb, key: "verb" },
                { label: "Timeline", value: dir.timeline_explicit || dir.timeline_inferred || "None mentioned", key: "time" }
              ].map((field) => (
                <div key={field.key} className="flex items-center justify-between group">
                  <div className="w-1/3 text-sm font-semibold text-gray-500 uppercase tracking-wider">{field.label}</div>
                  <input 
                    className="w-1/2 border border-gray-200 rounded p-2 text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none transition-all" 
                    defaultValue={field.value} 
                  />
                  <button 
                    onClick={() => toggleApproval(idx, field.key)} 
                    className={`p-1.5 rounded-md transition-colors ${verifiedFields[`${idx}-${field.key}`] ? 'bg-green-100 text-green-700' : 'text-gray-400 hover:bg-gray-100'}`}>
                    <Check size={18} strokeWidth={verifiedFields[`${idx}-${field.key}`] ? 3 : 2}/>
                  </button>
                </div>
              ))}

              {/* Decision Engine Output */}
              <div className={`mt-6 p-4 rounded-md border ${dir.compliance_vs_appeal === 'APPEAL' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle size={18} className={dir.compliance_vs_appeal === 'APPEAL' ? 'text-red-600' : 'text-green-600'}/>
                  <span className="font-bold text-sm tracking-wide">AI Strategy: {dir.compliance_vs_appeal}</span>
                </div>
                <p className="text-sm text-gray-700 italic">"{dir.reasoning}"</p>
              </div>

              {/* Source Span Traceability */}
              <div className="text-xs text-gray-500 bg-gray-100 p-3 rounded-md mt-4 border border-gray-200">
                <span className="font-bold text-gray-700 block mb-1">Source Quote:</span> 
                "{dir.source_span?.exact_text || "No exact text available."}"
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
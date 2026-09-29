import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { FileText, Upload, FileCheck, Brain, CheckCircle2 } from 'lucide-react';

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [resultMessage, setResultMessage] = useState(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const data = await api.getDocuments();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    try {
      setUploading(true);
      setResultMessage(null);
      const res = await api.uploadDocument(file);
      setResultMessage(
        `Uploaded & Processed '${res.document.name}'. Extracted ${res.processing.facts_extracted} memory facts into Hindsight bank!`
      );
      setFile(null);
      await loadDocuments();
    } catch (err) {
      console.error(err);
      setResultMessage('Failed uploading file. Please ensure file format is PDF, DOCX, TXT, or CSV.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <FileText className="w-6 h-6 text-blue-600" />
          Audit Document Ingestion & Processing
        </h2>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Upload PDF, DOCX, TXT, or CSV reports to extract historical facts into Hindsight persistent memory.
        </p>
      </div>

      {/* Upload Drag & Drop Area */}
      <div className="bg-white border-2 border-dashed border-blue-200 hover:border-blue-500 rounded-3xl p-8 text-center space-y-4 transition-all shadow-xs">
        <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto border border-blue-100">
          <Upload className="w-6 h-6" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-slate-900">Select Audit Document File</h3>
          <p className="text-xs text-slate-500 mt-1 font-medium">Supports PDF, DOCX, TXT, CSV (Max 25MB)</p>
        </div>

        <form onSubmit={handleUpload} className="flex flex-col items-center gap-3">
          <input
            type="file"
            accept=".pdf,.docx,.txt,.csv"
            onChange={(e) => setFile(e.target.files[0])}
            className="text-xs text-slate-600 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
          />

          {file && (
            <button
              type="submit"
              disabled={uploading}
              className="px-6 py-2.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/20 transition-all"
            >
              <Brain className="w-4 h-4" />
              {uploading ? 'Extracting Memory Facts...' : 'Process & Push to Hindsight Memory'}
            </button>
          )}
        </form>

        {resultMessage && (
          <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 max-w-lg mx-auto flex items-center justify-center gap-2 font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            {resultMessage}
          </div>
        )}
      </div>

      {/* Documents Table */}
      <div className="bg-white border border-slate-200/80 rounded-3xl overflow-hidden shadow-xs">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-bold text-slate-900 text-sm">Ingested Organizational Documents</h3>
          <span className="text-xs text-slate-500 font-semibold">Total: {documents.length}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase font-bold text-[10px] tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-6 py-4">Document Name</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Size</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Hindsight Facts Retained</th>
                <th className="px-6 py-4">Uploaded At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 font-medium">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-blue-50/40 transition-colors">
                  <td className="px-6 py-4 font-bold text-slate-900 flex items-center gap-2">
                    <FileCheck className="w-4 h-4 text-blue-600" />
                    {doc.name}
                  </td>
                  <td className="px-6 py-4 font-mono text-[11px] text-slate-500">{doc.file_type}</td>
                  <td className="px-6 py-4 text-slate-500">{(doc.file_size / 1024).toFixed(1)} KB</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-extrabold">
                      Processed
                    </span>
                  </td>
                  <td className="px-6 py-4 font-extrabold text-blue-700 font-mono">
                    {doc.facts_extracted} Memory Nodes
                  </td>
                  <td className="px-6 py-4 text-slate-500 font-mono text-[11px]">
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

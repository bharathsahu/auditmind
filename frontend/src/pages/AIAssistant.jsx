import React, { useState } from 'react';
import { api } from '../services/api';
import { Bot, Send, User, Sparkles, History, MessageSquareHeart, Smile, ExternalLink, ShieldCheck } from 'lucide-react';

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: "👋 Hi there! I'm your **AI Audit & Compliance Companion**.\n\nYou can talk to me in natural human language! Ask me anything about our past audits, recurring problems, high-risk controls, or who is working on remediations.\n\nI connect directly to **Hindsight Persistent Organizational Memory** to remember everything across 2024, 2025, and 2026.\n\nHow can I help you today?",
      memories: [],
      citations: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const friendlyPrompts = [
    "Hey! Did we have any transaction approval issues in previous audits?",
    "Can you tell me which remediation actions are overdue?",
    "What are our highest risk findings right now?",
    "Who is responsible for fixing our active control exceptions?"
  ];

  const handleSend = async (textToSend) => {
    const queryText = textToSend || input;
    if (!queryText.trim() || loading) return;

    const userMsg = { sender: 'user', text: queryText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.askAI(queryText);
      const assistantMsg = {
        sender: 'assistant',
        text: res.response,
        memories: res.recalled_memories || [],
        citations: res.citations || []
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: "Oops! I ran into a minor connection glitch. Please ensure the backend server is running smoothly."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-[calc(100vh-4rem)] flex flex-col justify-between">
      {/* Top Title Banner */}
      <div className="border-b border-slate-200 pb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20">
            <MessageSquareHeart className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              Friendly AI Audit Companion
            </h2>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Grounded AI reasoning • Powered by <strong>Hindsight Memory Layer</strong>
            </p>
          </div>
        </div>

        <div className="px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 flex items-center gap-2 text-xs text-blue-900 font-bold">
          <ShieldCheck className="w-4 h-4 text-blue-600" />
          <span>Grounded Citations: <strong className="text-blue-700 font-mono">Active</strong></span>
        </div>
      </div>

      {/* Friendly Prompts */}
      <div className="flex flex-wrap gap-2 my-4">
        {friendlyPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            className="px-3.5 py-2 rounded-2xl bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-300 text-xs text-slate-700 font-semibold transition-all flex items-center gap-2 shadow-xs text-left"
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-600 shrink-0" />
            <span>"{prompt}"</span>
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 my-2">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex items-start gap-3 text-xs ${
              msg.sender === 'user' ? 'flex-row-reverse' : ''
            }`}
          >
            <div
              className={`w-9 h-9 rounded-2xl flex items-center justify-center font-bold shrink-0 shadow-xs border ${
                msg.sender === 'user'
                  ? 'bg-blue-600 border-blue-500 text-white'
                  : 'bg-white border-slate-200 text-blue-600'
              }`}
            >
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`space-y-2 max-w-2xl ${msg.sender === 'user' ? 'text-right' : ''}`}>
              <div
                className={`p-4 rounded-3xl border text-slate-800 leading-relaxed whitespace-pre-line shadow-xs ${
                  msg.sender === 'user'
                    ? 'bg-blue-600 text-white font-medium border-blue-500'
                    : 'bg-white border-slate-200/80 font-medium'
                }`}
              >
                {msg.text}
              </div>

              {/* Grounded Source Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 text-left">
                  <div className="text-[10px] uppercase font-bold text-slate-700 tracking-wider flex items-center gap-1.5">
                    <ExternalLink className="w-3.5 h-3.5 text-blue-600" />
                    Grounded Source Citations ({msg.citations.length})
                  </div>
                  <div className="grid grid-cols-1 gap-1.5">
                    {msg.citations.map((c, cidx) => (
                      <div key={cidx} className="text-[11px] text-slate-700 bg-white p-2.5 rounded-xl border border-slate-200/80 flex items-start gap-2">
                        <span className="px-1.5 py-0.5 rounded-md bg-blue-100 text-blue-800 text-[10px] font-bold shrink-0">{c.code}</span>
                        <div>
                          <strong className="text-slate-900">{c.title}</strong>
                          <p className="text-[10px] text-slate-500 mt-0.5 line-clamp-1">{c.snippet}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recalled Memories Pills */}
              {msg.memories && msg.memories.length > 0 && (
                <div className="p-3 rounded-2xl bg-blue-50/80 border border-blue-200/80 space-y-1.5 text-left">
                  <div className="text-[10px] uppercase font-bold text-blue-900 tracking-wider flex items-center gap-1.5">
                    <History className="w-3.5 h-3.5 text-blue-600" />
                    Hindsight Recalled Memories ({msg.memories.length})
                  </div>
                  <div className="space-y-1">
                    {msg.memories.map((m, midx) => (
                      <div key={midx} className="text-[11px] text-slate-800 font-mono bg-white p-2 rounded-xl border border-slate-200/80">
                        [{m.year}] <strong className="text-blue-700">{m.reference_code}</strong>: {m.content}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-slate-500 text-xs py-2 font-medium">
            <div className="w-8 h-8 rounded-xl bg-white border border-slate-200 flex items-center justify-center">
              <Bot className="w-4 h-4 text-blue-600 animate-spin" />
            </div>
            <span>Thinking and retrieving Hindsight organizational memory...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="pt-3 border-t border-slate-200">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask me anything in plain human language (e.g., 'Hey, did anyone miss transaction sign-offs in 2024?')..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-white border border-slate-200 rounded-2xl px-4 py-3.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 shadow-xs font-medium"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3.5 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-blue-600/20 disabled:opacity-50 transition-all"
          >
            <span>Ask AI</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}

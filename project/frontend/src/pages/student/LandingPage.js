import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Bot, BookOpen, FileText, MessageSquare, ShieldCheck,
  Zap, Database, ArrowRight, GraduationCap, Building2, ChevronRight
} from 'lucide-react';

const FloatingOrb = ({ className, size, color }) => (
  <div className={`orb ${className}`}
    style={{ width: size, height: size, background: color, opacity: 0.15 }} />
);

const FeatureCard = ({ icon: Icon, title, desc, color, delay }) => (
  <div className="card group hover:border-primary-500/30 transition-all duration-300 cursor-default"
    style={{ animationDelay: delay, animation: 'slideUp 0.5s ease-out forwards', opacity: 0 }}>
    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-4`}
      style={{ background: `${color}20`, border: `1px solid ${color}30` }}>
      <Icon size={18} style={{ color }} />
    </div>
    <h3 className="font-display font-semibold text-white text-base mb-2">{title}</h3>
    <p className="font-body text-sm text-gray-500 leading-relaxed">{desc}</p>
  </div>
);

const Step = ({ num, label, sub }) => (
  <div className="flex items-start gap-3">
    <div className="w-7 h-7 rounded-full bg-primary-600/30 border border-primary-500/40 flex items-center justify-center flex-shrink-0 mt-0.5">
      <span className="text-primary-400 text-xs font-display font-bold">{num}</span>
    </div>
    <div>
      <p className="text-white text-sm font-display font-medium">{label}</p>
      <p className="text-gray-500 text-xs font-body mt-0.5">{sub}</p>
    </div>
  </div>
);

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-0 relative overflow-hidden">
      {/* Background orbs */}
      <FloatingOrb className="top-[-100px] left-[-100px]" size="500px" color="#6366f1" />
      <FloatingOrb className="top-[300px] right-[-150px]" size="400px" color="#8b5cf6" />
      <FloatingOrb className="bottom-[-200px] left-[30%]" size="600px" color="#06b6d4" />

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-6xl mx-auto">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <Bot size={16} className="text-white" />
          </div>
          <span className="font-display font-bold text-white text-base tracking-tight">DeptAI</span>
          <span className="badge bg-primary-600/20 text-primary-400 border border-primary-500/30 ml-1">Beta</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/admin/login" className="text-gray-400 hover:text-gray-200 text-sm font-body transition-colors">
            Admin
          </Link>
          <Link to="/login" className="btn-ghost text-sm py-2 px-4">Sign in</Link>
          <Link to="/signup" className="btn-primary text-sm py-2 px-4">Get Started <ArrowRight size={14} /></Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pt-16 pb-20">
        <div className="text-center max-w-3xl mx-auto">
          {/* Eyebrow */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-white/10 text-xs font-body text-gray-400 mb-8"
            style={{ animation: 'fadeIn 0.4s ease-out forwards' }}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Powered by Ollama · Fully Local · No Data Leaves Campus
          </div>

          <h1 className="font-display font-extrabold text-5xl md:text-6xl text-white leading-[1.1] tracking-tight mb-6"
            style={{ animation: 'slideUp 0.5s 0.1s ease-out forwards', opacity: 0 }}>
            Your Department's
            <br />
            <span className="bg-gradient-to-r from-primary-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
              AI Intelligence
            </span>
          </h1>

          <p className="font-body text-gray-400 text-lg leading-relaxed mb-10 max-w-2xl mx-auto"
            style={{ animation: 'slideUp 0.5s 0.2s ease-out forwards', opacity: 0 }}>
            Instant answers to department queries — FAQs, procedures, notices, and documents.
            Backed by RAG and local LLMs. No hallucinations, no out-of-scope nonsense.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap"
            style={{ animation: 'slideUp 0.5s 0.3s ease-out forwards', opacity: 0 }}>
            <Link to="/signup" className="btn-primary px-7 py-3 text-base">
              Start Chatting <ArrowRight size={16} />
            </Link>
            <Link to="/login" className="btn-ghost px-7 py-3 text-base">
              I have an account
            </Link>
          </div>
        </div>

        {/* Chat preview mockup */}
        <div className="mt-16 max-w-2xl mx-auto"
          style={{ animation: 'slideUp 0.6s 0.4s ease-out forwards', opacity: 0 }}>
          <div className="glass-dark rounded-2xl border border-white/8 overflow-hidden">
            {/* Window chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/8 bg-surface-1/50">
              <div className="w-2.5 h-2.5 rounded-full bg-rose-500/70" />
              <div className="w-2.5 h-2.5 rounded-full bg-amber-500/70" />
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/70" />
              <div className="flex items-center gap-1.5 ml-3">
                <Bot size={12} className="text-primary-400" />
                <span className="text-xs font-mono text-gray-500">DeptAI Chat</span>
              </div>
            </div>
            {/* Chat messages */}
            <div className="p-5 space-y-4 bg-surface-1/30">
              <div className="flex gap-3 items-start">
                <div className="w-7 h-7 rounded-full bg-primary-600/30 border border-primary-500/30 flex items-center justify-center flex-shrink-0">
                  <Bot size={13} className="text-primary-400" />
                </div>
                <div className="chat-bubble-ai !ml-0">
                  Welcome! I'm your department assistant. I can answer questions about courses, procedures, faculty, and notices. How can I help you today?
                </div>
              </div>
              <div className="chat-bubble-user">
                What are the thesis submission deadlines for this semester?
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-7 h-7 rounded-full bg-primary-600/30 border border-primary-500/30 flex items-center justify-center flex-shrink-0">
                  <Bot size={13} className="text-primary-400" />
                </div>
                <div className="chat-bubble-ai !ml-0">
                  Based on the department notices, the thesis submission deadline for Fall 2025 is <span className="text-primary-400 font-medium">December 15, 2025</span>. You must submit a soft copy via the portal and a hard copy to the department office. Late submissions require written approval from your supervisor.
                </div>
              </div>
              <div className="flex gap-2 items-center pl-10">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features grid */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-12">
          <h2 className="font-display font-bold text-3xl text-white mb-3">Built for Academic Departments</h2>
          <p className="text-gray-500 font-body">A purpose-built system — not a generic chatbot</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FeatureCard icon={Database} title="RAG-Powered Retrieval" color="#6366f1"
            desc="Semantic search over department documents. Finds relevant context even with different phrasing."
            delay="0.1s" />
          <FeatureCard icon={ShieldCheck} title="Domain Restricted" color="#10b981"
            desc="Strictly answers department-related queries. Rejects out-of-scope questions automatically."
            delay="0.2s" />
          <FeatureCard icon={Zap} title="Local LLM (Ollama)" color="#f59e0b"
            desc="Runs entirely on-premises. No external API calls. Your data stays in your infrastructure."
            delay="0.3s" />
          <FeatureCard icon={BookOpen} title="Structured Knowledge" color="#06b6d4"
            desc="FAQs, procedures, and notices managed by admins. Always up-to-date and authoritative."
            delay="0.4s" />
          <FeatureCard icon={FileText} title="Document Ingestion" color="#8b5cf6"
            desc="Upload PDFs, DOCX files. Auto-chunked, embedded, and indexed into FAISS vector store."
            delay="0.5s" />
          <FeatureCard icon={MessageSquare} title="Context-Aware Responses" color="#f43f5e"
            desc="Responses grounded in retrieved documents. Cites sources. Minimal hallucination risk."
            delay="0.6s" />
        </div>
      </section>

      {/* How it works */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        <div className="glass-dark rounded-2xl p-8 md:p-12 border border-white/8">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div>
              <h2 className="font-display font-bold text-2xl text-white mb-2">How It Works</h2>
              <p className="text-gray-500 font-body text-sm mb-8">Hybrid pipeline combining structured knowledge with semantic retrieval</p>
              <div className="space-y-5">
                <Step num="1" label="You ask a question" sub="Natural language — no special commands needed" />
                <Step num="2" label="Domain check runs" sub="Ensures query is department-relevant" />
                <Step num="3" label="Hybrid retrieval" sub="Structured FAQs + semantic FAISS search" />
                <Step num="4" label="LLM generates response" sub="Ollama synthesizes context into a clear answer" />
              </div>
            </div>
            <div className="space-y-3">
              {[
                { icon: GraduationCap, label: 'Student Portal', desc: 'Login · Chat · Get answers', color: '#6366f1' },
                { icon: Building2, label: 'Admin Dashboard', desc: 'Manage knowledge · Upload docs · View logs', color: '#8b5cf6' },
                { icon: Database, label: 'RAG Pipeline', desc: 'FAISS · SentenceTransformers · Ollama', color: '#06b6d4' },
              ].map(({ icon: Icon, label, desc, color }) => (
                <div key={label} className="flex items-center gap-4 p-4 rounded-xl bg-white/3 border border-white/8 hover:border-white/15 transition-colors">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: `${color}15`, border: `1px solid ${color}25` }}>
                    <Icon size={18} style={{ color }} />
                  </div>
                  <div>
                    <p className="font-display font-semibold text-white text-sm">{label}</p>
                    <p className="font-mono text-xs text-gray-500">{desc}</p>
                  </div>
                  <ChevronRight size={14} className="text-gray-600 ml-auto" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-12 text-center">
        <h2 className="font-display font-bold text-2xl text-white mb-3">Ready to get started?</h2>
        <p className="text-gray-500 font-body text-sm mb-6">Sign up with your department email to access the AI assistant</p>
        <Link to="/signup" className="btn-primary mx-auto px-8 py-3 text-base w-fit">
          Create Student Account <ArrowRight size={16} />
        </Link>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/8 py-8 text-center">
        <p className="text-gray-600 font-body text-xs">
          Department AI Assistant · Built with React, FastAPI, Ollama, FAISS ·
          <span className="text-gray-500"> For internal academic use only</span>
        </p>
      </footer>
    </div>
  );
}

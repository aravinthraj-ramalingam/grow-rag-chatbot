import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Sparkles, BarChart3, ShieldCheck, UserCheck, Zap, Send, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const FeatureCard = ({ icon: Icon, title, desc }) => (
  <motion.div
    whileHover={{ y: -5 }}
    className="glass glass-hover p-6 rounded-3xl"
  >
    <div className="flex items-start gap-4">
      <div className="p-3 bg-blue-500/10 rounded-2xl">
        <Icon className="w-6 h-6 text-blue-500" />
      </div>
      <div>
        <h3 className="font-semibold text-lg text-white mb-1">{title}</h3>
        <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
      </div>
    </div>
  </motion.div>
);

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || '';
      const response = await axios.post(`${backendUrl}/api/chat`, { query: input });
      const botMsg = { role: 'assistant', content: response.data.answer };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'system', content: 'Connection failed. Ensure backend is running.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 pt-12 pb-32 min-h-screen flex flex-col">
      {/* Header Section */}
      <header className="text-center mb-12">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative inline-block mb-6"
        >
          <div className="absolute inset-0 bg-blue-500/30 blur-3xl rounded-full scale-150 animate-pulse" />
          <div className="relative glass p-4 rounded-full border-blue-500/30">
            <Sparkles className="w-12 h-12 text-blue-500" />
          </div>
        </motion.div>

        <h1 className="text-5xl md:text-6xl font-bold glow-text tracking-tight mb-4">
          Groww Assistant
        </h1>
        <p className="text-lg md:text-xl text-gray-400 font-light max-w-2xl mx-auto">
          Facts-only assistant for Tata Mutual Fund details. <span className="text-blue-500/80 font-normal underline decoration-blue-500/30 underline-offset-4">No investment advice.</span>
        </p>
      </header>

      {/* Feature Grid - Only show when no messages */}
      <AnimatePresence>
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12"
          >
            <FeatureCard
              icon={BarChart3}
              title="NAV & Analytics"
              desc="Real-time NAV and benchmark performance tracking."
            />
            <FeatureCard
              icon={ShieldCheck}
              title="Risk & Tax"
              desc="Exit Loads, Stamp Duty, and post-tax efficiency."
            />
            <FeatureCard
              icon={UserCheck}
              title="Fund Management"
              desc="Strategic tenure and experience of fund managers."
            />
            <FeatureCard
              icon={Zap}
              title="Quick Liquidity"
              desc="Minimum SIP/Lump Sum and redemption turnaround."
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat History Section */}
      <div className="flex-1 space-y-6 mb-8 overflow-y-auto max-h-[50vh] scrollbar-hide">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[85%] p-5 rounded-3xl ${msg.role === 'user'
              ? 'bg-blue-600 text-white rounded-tr-none'
              : 'glass text-gray-100 rounded-tl-none border-white/5 shadow-2xl'
              }`}>
              <p className="text-sm leading-relaxed whitespace-pre-line">{msg.content}</p>
            </div>
          </motion.div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="glass p-4 rounded-3xl rounded-tl-none flex items-center gap-3">
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
              <span className="text-xs text-gray-400 font-light uppercase tracking-wider">Analyzing Context...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Section */}
      <footer className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6">
        <form onSubmit={handleSend} className="relative group">
          <div className="absolute inset-0 bg-blue-500/20 blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity" />
          <div className="relative glass p-2 rounded-full border-white/10 group-focus-within:border-blue-500/50 flex items-center transition-all duration-300 shadow-2xl">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Query any Tata Mutual Fund fact..."
              className="flex-1 bg-transparent px-6 py-2 outline-none text-white text-sm placeholder:text-gray-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="p-3 rounded-full hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100"
              style={{ background: 'linear-gradient(135deg, #5669ff 0%, #04b488 100%)' }}
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </form>
        <p className="text-[10px] text-center mt-4 text-gray-600 font-light uppercase tracking-[0.2em]">
          Grounded context • No Investment Advice
        </p>
      </footer>
    </div>
  );
};

export default App;

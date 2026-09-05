import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles, RefreshCw, Leaf } from 'lucide-react';

export default function AgroBot({ activeContext, selectedLanguage }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: `🌾 **Hello! I am AgroBot, your AI Agricultural & Pest Advisory Assistant.**\n\nHow can I help you today? You can ask me about crop diseases, organic bio-controls, fertilizer dosage, or pesticide spraying schedules.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputMsg, setInputMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (activeContext) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: `🔍 **Context Loaded:** I see you just diagnosed **${activeContext}**. Ask me any question about organic remedies, chemical dosage, or field management for this crop!`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  }, [activeContext]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || inputMsg;
    if (!query.trim()) return;

    const userMsgObj = {
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsgObj]);
    if (!textToSend) setInputMsg('');
    setLoading(true);

    try {
      
      const res = await fetch('http://127.0.0.1:8000/api/agri-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          disease_class: activeContext || 'General Query',
          language: selectedLanguage
        })
      });

      const data = await res.json();
      const botMsgObj = {
        sender: 'bot',
        text: data.answer || 'Apologies, could not process query. Please try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botMsgObj]);
    } catch (err) {
      console.error("AgroBot Chat Error:", err);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: '⚠️ Connection error. Please ensure the backend server is running.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "How to prepare 5% Neem Oil spray?",
    "Is it safe to spray pesticides today?",
    "Organic remedies for Late Blight",
    "Balanced NPK fertilizer ratio"
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '900px', margin: '0 auto' }}>
      
      {/* Header */}
      <div className="warm-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #7a8b75 0%, #556650 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff'
          }}>
            <Bot size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: '700', color: '#3a3532' }}>AgroBot AI Advisory</h2>
            <p style={{ fontSize: '0.82rem', color: '#827a74' }}>
              Conversational ChatGPT-style Agronomic Assistant ({selectedLanguage})
            </p>
          </div>
        </div>

        {activeContext && (
          <span className="badge-pill badge-healthy" style={{ fontSize: '0.78rem' }}>
            <Leaf size={14} /> Context: {activeContext}
          </span>
        )}
      </div>

      {/* Chat Window */}
      <div className="warm-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', minHeight: '480px', maxHeight: '600px', overflowY: 'auto' }}>
        
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                gap: '12px',
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%'
              }}
            >
              {msg.sender === 'bot' && (
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#7a8b75', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Bot size={18} />
                </div>
              )}

              <div style={{
                background: msg.sender === 'user' ? 'linear-gradient(135deg, #c67d63 0%, #b46b52 100%)' : '#f5efe6',
                color: msg.sender === 'user' ? '#ffffff' : '#3a3532',
                border: msg.sender === 'user' ? 'none' : '1px solid #e6dcce',
                borderRadius: msg.sender === 'user' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                padding: '14px 18px',
                fontSize: '0.92rem',
                lineHeight: '1.5',
                whiteSpace: 'pre-wrap',
                boxShadow: '0 2px 10px rgba(180, 150, 120, 0.08)'
              }}>
                {msg.text}
                <div style={{ fontSize: '0.7rem', color: msg.sender === 'user' ? 'rgba(255,255,255,0.7)' : '#827a74', marginTop: '6px', textAlign: 'right' }}>
                  {msg.timestamp}
                </div>
              </div>

              {msg.sender === 'user' && (
                <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#c67d63', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <User size={18} />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#827a74', fontSize: '0.85rem' }}>
              <RefreshCw className="animate-spin" size={16} color="#7a8b75" /> AgroBot is synthesizing expert advisory...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Quick Prompts */}
        <div style={{ marginTop: '20px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {quickPrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => handleSendMessage(p)}
              style={{
                background: '#ffffff',
                border: '1px solid #e6dcce',
                color: '#3a3532',
                fontSize: '0.78rem',
                fontWeight: '600',
                padding: '6px 14px',
                borderRadius: '50px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              💡 {p}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div style={{ marginTop: '16px', display: 'flex', gap: '10px' }}>
          <input
            type="text"
            placeholder={`Ask AgroBot any farming or treatment query in ${selectedLanguage}...`}
            value={inputMsg}
            onChange={(e) => setInputMsg(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            style={{
              flex: 1,
              background: '#ffffff',
              border: '1px solid #e6dcce',
              borderRadius: '50px',
              padding: '12px 20px',
              fontSize: '0.9rem',
              color: '#3a3532',
              outline: 'none'
            }}
          />
          <button onClick={() => handleSendMessage()} disabled={loading} className="btn-pill-primary">
            <Send size={18} />
          </button>
        </div>

      </div>

    </div>
  );
}

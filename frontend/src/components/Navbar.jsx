import React from 'react';
import { Sprout, Globe, Home, Sparkles, MessageSquare, Info, ShieldAlert } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, selectedLang, setSelectedLang }) {
  const languages = [
    { code: "Hindi", name: "Hindi (हिंदी)" },
    { code: "Khortha", name: "Khortha (खोरठा)" },
    { code: "Nagpuri", name: "Nagpuri (नागपुरी)" },
    { code: "Bhojpuri", name: "Bhojpuri (भोजपुरी)" },
    { code: "English", name: "English" },
    { code: "Bengali", name: "Bengali (বাংলা)" },
    { code: "Marathi", name: "Marathi (मराठी)" },
    { code: "Telugu", name: "Telugu (తెలుగు)" },
    { code: "Tamil", name: "Tamil (தமிழ்)" },
    { code: "Gujarati", name: "Gujarati (ગુજરાતી)" }
  ];

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'detection', label: 'Disease Detection', icon: Sparkles },
    { id: 'agrobot', label: 'AI Advisory', icon: MessageSquare },
    { id: 'about', label: 'About', icon: Info },
    { id: 'sdg', label: 'SDG & Impact', icon: ShieldAlert }
  ];

  return (
    <header style={{
      background: 'rgba(251, 248, 243, 0.95)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid #e6dcce',
      padding: '16px 32px',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }} onClick={() => setActiveTab('home')}>
          <div style={{
            background: 'linear-gradient(135deg, #c67d63 0%, #b46b52 100%)',
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 4px 14px rgba(198, 125, 99, 0.3)'
          }}>
            <Sprout size={22} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.3rem', fontWeight: '800', color: '#3a3532', letterSpacing: '0.3px' }}>
              FasalRakshak
            </h1>
            <span style={{ fontSize: '0.72rem', color: '#827a74', letterSpacing: '1px', textTransform: 'uppercase' }}>
              AI Precision Agriculture
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  background: isActive ? '#ffffff' : 'transparent',
                  color: isActive ? '#c67d63' : '#827a74',
                  border: isActive ? '1px solid #e6dcce' : '1px solid transparent',
                  padding: '8px 18px',
                  borderRadius: '50px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.88rem',
                  boxShadow: isActive ? '0 2px 10px rgba(180, 150, 120, 0.1)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Regional Language Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Globe size={18} color="#c67d63" />
          <select
            value={selectedLang}
            onChange={(e) => setSelectedLang(e.target.value)}
            style={{
              background: '#ffffff',
              color: '#3a3532',
              border: '1px solid #e6dcce',
              borderRadius: '50px',
              padding: '6px 16px',
              fontSize: '0.85rem',
              fontWeight: '600',
              cursor: 'pointer',
              outline: 'none',
              boxShadow: '0 2px 8px rgba(180, 150, 120, 0.08)'
            }}
          >
            {languages.map((l) => (
              <option key={l.code} value={l.code}>
                {l.name}
              </option>
            ))}
          </select>
        </div>

      </div>
    </header>
  );
}

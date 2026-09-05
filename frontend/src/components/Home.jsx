import React from 'react';
import { Sparkles, MessageSquare, CloudRain, ShieldCheck, Sprout, ArrowRight, Activity } from 'lucide-react';

export default function Home({ onNavigate }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '36px' }}>
      
      {/* Hero Section */}
      <div className="warm-card" style={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f5efe6 100%)',
        textAlign: 'center',
        padding: '56px 32px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(198, 125, 99, 0.12)',
          color: '#c67d63',
          padding: '6px 18px',
          borderRadius: '50px',
          fontSize: '0.85rem',
          fontWeight: '700',
          marginBottom: '20px',
          border: '1px solid rgba(198, 125, 99, 0.3)'
        }}>
          <Sprout size={16} /> Precision Deep Learning & Agricultural AI
        </div>

        <h1 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: '3rem',
          fontWeight: '700',
          color: '#3a3532',
          lineHeight: '1.25',
          marginBottom: '16px',
          maxWidth: '820px',
          margin: '0 auto 16px auto'
        }}>
          Protect Your Crops with AI-Powered Pathology & Real-Time Voice Advisory
        </h1>

        <p style={{
          fontSize: '1.1rem',
          color: '#827a74',
          maxWidth: '680px',
          margin: '0 auto 32px auto',
          lineHeight: '1.6'
        }}>
          Instant leaf disease diagnosis using deep convolutional neural networks, real-time micro-climate spray warnings, and conversational AI guidance in 14 regional languages.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <button onClick={() => onNavigate('detection')} className="btn-pill-primary" style={{ padding: '14px 36px', fontSize: '1rem' }}>
            <Sparkles size={20} /> Detect Crop Disease Now
          </button>
          <button onClick={() => onNavigate('agrobot')} className="btn-pill-secondary" style={{ padding: '14px 36px', fontSize: '1rem' }}>
            <MessageSquare size={20} /> Chat with AgroBot
          </button>
        </div>
      </div>

      {/* Feature Quick Action Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        
        <div className="warm-card" style={{ borderTop: '4px solid #c67d63', cursor: 'pointer' }} onClick={() => onNavigate('detection')}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(198, 125, 99, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#c67d63', marginBottom: '16px' }}>
            <Sparkles size={24} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#3a3532', marginBottom: '8px' }}>
            Real-Time Disease Detection
          </h3>
          <p style={{ fontSize: '0.88rem', color: '#827a74', lineHeight: '1.5', marginBottom: '16px' }}>
            Upload crop leaf photos to identify blights, rusts, and leaf spots with confidence metrics and Grad-CAM visual heatmaps.
          </p>
          <span style={{ fontSize: '0.88rem', fontWeight: '700', color: '#c67d63', display: 'flex', alignItems: 'center', gap: '6px' }}>
            Try Disease Detection <ArrowRight size={16} />
          </span>
        </div>

        <div className="warm-card" style={{ borderTop: '4px solid #7a8b75', cursor: 'pointer' }} onClick={() => onNavigate('agrobot')}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(122, 139, 117, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#7a8b75', marginBottom: '16px' }}>
            <MessageSquare size={24} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#3a3532', marginBottom: '8px' }}>
            AgroBot ChatGPT AI Assistant
          </h3>
          <p style={{ fontSize: '0.88rem', color: '#827a74', lineHeight: '1.5', marginBottom: '16px' }}>
            Conversational AI assistant for customized fertilizer dosage, organic bio-control preparation, and pesticide spraying steps.
          </p>
          <span style={{ fontSize: '0.88rem', fontWeight: '700', color: '#7a8b75', display: 'flex', alignItems: 'center', gap: '6px' }}>
            Ask AgroBot <ArrowRight size={16} />
          </span>
        </div>

        <div className="warm-card" style={{ borderTop: '4px solid #8c633a', cursor: 'pointer' }} onClick={() => onNavigate('sdg')}>
          <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(217, 180, 143, 0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8c633a', marginBottom: '16px' }}>
            <ShieldCheck size={24} />
          </div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#3a3532', marginBottom: '8px' }}>
            Micro-Climate Spray Advisory
          </h3>
          <p style={{ fontSize: '0.88rem', color: '#827a74', lineHeight: '1.5', marginBottom: '16px' }}>
            Real-time weather tracking warns farmers against spraying before rain or high wind to prevent pesticide runoff.
          </p>
          <span style={{ fontSize: '0.88rem', fontWeight: '700', color: '#8c633a', display: 'flex', alignItems: 'center', gap: '6px' }}>
            Explore SDG & Impact <ArrowRight size={16} />
          </span>
        </div>

      </div>

    </div>
  );
}

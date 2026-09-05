import React from 'react';
import { Cpu, ShieldCheck, Globe, Thermometer, Layers, Award } from 'lucide-react';

export default function About() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header Card */}
      <div className="warm-card" style={{ borderTop: '4px solid #c67d63' }}>
        <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.8rem', fontWeight: '600', color: '#3a3532', marginBottom: '8px' }}>
          About FasalRakshak AI
        </h2>
        <p style={{ fontSize: '0.92rem', color: '#827a74', lineHeight: '1.6' }}>
          FasalRakshak is an advanced precision agricultural health platform designed to help smallholder farmers and agronomic researchers diagnose crop leaf diseases, receive localized voice remedies, and practice sustainable farming.
        </p>
      </div>

      {/* Core Technology Pillars */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        
        <div className="warm-card-sm">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#c67d63', fontWeight: '700' }}>
            <Cpu size={20} /> MobileNetV3 Neural Engine
          </div>
          <p style={{ fontSize: '0.85rem', color: '#655e58', lineHeight: '1.5' }}>
            Lightweight deep convolutional neural network optimized for real-time edge pathology classification with low CPU latency and high diagnostic accuracy.
          </p>
        </div>

        <div className="warm-card-sm">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#7a8b75', fontWeight: '700' }}>
            <Layers size={20} /> Grad-CAM Explainability
          </div>
          <p style={{ fontSize: '0.85rem', color: '#655e58', lineHeight: '1.5' }}>
            Generates visual saliency heatmaps highlighting exact leaf lesions and necrotic spots triggering neural classification for transparent AI reasoning.
          </p>
        </div>

        <div className="warm-card-sm">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#8c633a', fontWeight: '700' }}>
            <Thermometer size={20} /> Micro-Climate Advisory
          </div>
          <p style={{ fontSize: '0.85rem', color: '#655e58', lineHeight: '1.5' }}>
            Integrates real-time district weather metrics (temp, humidity, rain %, wind speed) to warn farmers against spraying pesticides before heavy rainfall or high wind.
          </p>
        </div>

        <div className="warm-card-sm">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#c67d63', fontWeight: '700' }}>
            <Globe size={20} /> Regional Multilingual Voice
          </div>
          <p style={{ fontSize: '0.85rem', color: '#655e58', lineHeight: '1.5' }}>
            Synthesizes natural, human-realistic regional audio remedies in 14 languages, eliminating literacy barriers for smallholder rural farmers.
          </p>
        </div>

      </div>

    </div>
  );
}

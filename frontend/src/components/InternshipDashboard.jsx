import React from 'react';
import { ShieldCheck, Target, Cpu, Scale, Lock, Eye, HeartHandshake, Award } from 'lucide-react';

export default function InternshipDashboard() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Internship Banner */}
      <div className="warm-card" style={{ borderTop: '4px solid #c67d63' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <Award size={28} color="#c67d63" />
          <div>
            <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.6rem', fontWeight: '600', color: '#3a3532' }}>
              1M1B AI for Sustainability Virtual Internship & NTCC Project
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#827a74' }}>
              In Collaboration with IBM SkillsBuild & AICTE &bull; AI + SDG Sustainability Guidelines
            </p>
          </div>
        </div>
      </div>

      {/* UN Sustainable Development Goals (SDGs) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        
        <div className="warm-card" style={{ borderTop: '4px solid #c67d63' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Target size={20} color="#c67d63" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#c67d63' }}>SDG 2: Zero Hunger</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#655e58', lineHeight: '1.5' }}>
            Early pathology detection saves 20–30% of crop yields from preventable blights, securing farm revenue and regional food supplies.
          </p>
        </div>

        <div className="warm-card" style={{ borderTop: '4px solid #7a8b75' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Target size={20} color="#7a8b75" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#7a8b75' }}>SDG 13: Climate Action</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#655e58', lineHeight: '1.5' }}>
            Real-time weather spray advisories warn farmers against spraying during rain or high wind, eliminating toxic chemical runoff.
          </p>
        </div>

        <div className="warm-card" style={{ borderTop: '4px solid #d9b48f' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Target size={20} color="#d9b48f" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#8c633a' }}>SDG 15: Life on Land</h3>
          </div>
          <p style={{ fontSize: '0.85rem', color: '#655e58', lineHeight: '1.5' }}>
            Prioritization of bio-fungicides (Neem oil 5%, <em>Trichoderma</em>) preserves soil microbiomes and protects pollinator honeybee colonies.
          </p>
        </div>

      </div>

      {/* IBM BOB & Granite RAG Pipeline */}
      <div className="warm-card">
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#3a3532', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Cpu size={20} color="#c67d63" />
          IBM BOB & IBM Granite RAG Workflow Pipeline
        </h3>
        
        <div style={{ background: '#f5efe6', padding: '20px', borderRadius: '16px', border: '1px solid #e6dcce', display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.88rem', color: '#3a3532' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge-tag">Input</span>
            <span>Crop Leaf Photograph + District Weather Metrics</span>
          </div>
          <div style={{ height: '1px', background: '#e6dcce' }}></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge-tag">Neural Model</span>
            <span>MobileNetV3 Classifier + Smart Leaf Guard Verification</span>
          </div>
          <div style={{ height: '1px', background: '#e6dcce' }}></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge-tag">IBM BOB RAG</span>
            <span>Vector Index Retrieval over Grounded ICAR & Web Agri Databases</span>
          </div>
          <div style={{ height: '1px', background: '#e6dcce' }}></div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge-tag">Voice Output</span>
            <span>Inworld AI High-Fidelity Regional Language Voice Synthesizer</span>
          </div>
        </div>
      </div>

      {/* Responsible AI Compliance */}
      <div className="warm-card">
        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#3a3532', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={20} color="#7a8b75" />
          Responsible AI Framework
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
          
          <div className="warm-card-sm">
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: '#c67d63', fontWeight: '700' }}>
              <Scale size={16} /> Fairness & Access
            </div>
            <p style={{ fontSize: '0.8rem', color: '#827a74' }}>
              Inworld AI regional voice synthesis in 10 languages removes literacy barriers for smallholder farmers.
            </p>
          </div>

          <div className="warm-card-sm">
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: '#7a8b75', fontWeight: '700' }}>
              <Eye size={16} /> Transparency
            </div>
            <p style={{ fontSize: '0.8rem', color: '#827a74' }}>
              Confidence scores and Grad-CAM visual heatmaps explain AI decisions. Low confidence triggers KVK escalation.
            </p>
          </div>

          <div className="warm-card-sm">
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: '#8c633a', fontWeight: '700' }}>
              <HeartHandshake size={16} /> Ethics
            </div>
            <p style={{ fontSize: '0.8rem', color: '#827a74' }}>
              Prioritizes organic bio-controls and safety pre-harvest intervals to prevent soil degradation and chemical runoff.
            </p>
          </div>

          <div className="warm-card-sm">
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', color: '#c67d63', fontWeight: '700' }}>
              <Lock size={16} /> Privacy
            </div>
            <p style={{ fontSize: '0.8rem', color: '#827a74' }}>
              Zero user data harvesting. Image evaluations execute locally without storing personal farmer profiles.
            </p>
          </div>

        </div>
      </div>

    </div>
  );
}

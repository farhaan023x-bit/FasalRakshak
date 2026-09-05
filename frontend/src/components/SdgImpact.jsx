import React from 'react';
import { Target, ShieldCheck, Scale, Eye, HeartHandshake, Lock } from 'lucide-react';

export default function SdgImpact() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header */}
      <div className="warm-card" style={{ borderTop: '4px solid #7a8b75' }}>
        <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.8rem', fontWeight: '600', color: '#3a3532', marginBottom: '8px' }}>
          Sustainability & SDG Impact
        </h2>
        <p style={{ fontSize: '0.9rem', color: '#827a74' }}>
          Aligning AI precision agriculture with global United Nations Sustainable Development Goals and Responsible AI principles.
        </p>
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
              Regional voice synthesis in 14 languages removes literacy barriers for smallholder farmers.
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

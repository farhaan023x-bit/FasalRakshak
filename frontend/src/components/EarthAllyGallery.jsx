import React, { useState, useEffect } from 'react';
import { BookOpen, Sparkles, CheckCircle } from 'lucide-react';

export default function EarthAllyGallery({ onSelectSample }) {
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSamples();
  }, []);

  const fetchSamples = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/samples');
      const data = await res.json();
      setSamples(data.samples || []);
    } catch (err) {
      console.error("Failed to fetch gallery:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="glass-card" style={{ textAlign: 'center', padding: '40px' }}>
        <p style={{ color: '#9ca3af' }}>Loading EarthAlly Pathology Dataset Gallery...</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#fff', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BookOpen size={24} color="#10b981" />
            EarthAlly Crop Pathology Sample Gallery
          </h2>
          <span className="badge-tag">1M1B Verified Dataset</span>
        </div>
        <p style={{ fontSize: '0.88rem', color: '#9ca3af' }}>
          Click any crop disease sample photo below to execute real-time MobileNetV3 pathology diagnosis & IBM BOB RAG synthesis.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '16px' }}>
        {samples.map((category) => (
          category.images.map((img) => (
            <div
              key={img.rel_path}
              className="glass-card-sm"
              style={{ cursor: 'pointer', transition: 'all 0.2s ease', position: 'relative' }}
              onClick={() => onSelectSample(img.rel_path, img.url)}
            >
              <img
                src={`http://127.0.0.1:8000${img.url}`}
                alt={category.disease}
                style={{ width: '100%', height: '180px', objectFit: 'cover', borderRadius: '10px', marginBottom: '12px' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fff' }}>
                    {category.crop}
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: '600' }}>
                    {category.disease}
                  </p>
                </div>
                <button className="btn-primary" style={{ padding: '6px 12px', fontSize: '0.78rem' }}>
                  <Sparkles size={14} /> Analyze
                </button>
              </div>
            </div>
          ))
        ))}
      </div>

    </div>
  );
}

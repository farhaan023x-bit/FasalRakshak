import React, { useState } from 'react';
import { Upload, Sparkles, Image as ImageIcon } from 'lucide-react';

export default function ImageUploadSection({ onAnalyze, loading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleRunAnalysis = () => {
    if (selectedFile) {
      onAnalyze({ type: 'file', payload: selectedFile });
    }
  };

  return (
    <div className="warm-card" style={{ textAlign: 'center' }}>
      
      {/* Title */}
      <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '2rem', color: '#3a3532', fontWeight: '600', marginBottom: '8px' }}>
        Upload Crop Leaf Image
      </h2>
      <p style={{ fontSize: '0.9rem', color: '#827a74', marginBottom: '24px', maxWidth: '540px', margin: '0 auto 24px auto' }}>
        Upload a photograph of any infected or healthy crop leaf. FasalRakshak AI will analyze visual pathology and retrieve grounded RAG remedies in real time.
      </p>

      {/* Drag & Drop Upload Zone */}
      <div
        style={{
          border: '2px dashed #d8cbba',
          borderRadius: '24px',
          padding: '40px 24px',
          background: '#f5efe6',
          cursor: 'pointer',
          position: 'relative',
          transition: 'all 0.2s ease',
          maxWidth: '600px',
          margin: '0 auto'
        }}
      >
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{
            position: 'absolute',
            top: 0, left: 0, width: '100%', height: '100%',
            opacity: 0, cursor: 'pointer'
          }}
        />
        
        <div style={{
          width: '54px',
          height: '54px',
          borderRadius: '50%',
          background: '#ffffff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 14px auto',
          boxShadow: '0 4px 12px rgba(180, 150, 120, 0.12)'
        }}>
          <Upload size={26} color="#c67d63" />
        </div>

        <p style={{ fontWeight: '700', color: '#3a3532', fontSize: '1rem' }}>
          Drag & Drop Crop Leaf Photo Here
        </p>
        <p style={{ fontSize: '0.82rem', color: '#827a74', marginTop: '6px' }}>
          or click to browse from device (JPG, PNG, WEBP)
        </p>
      </div>

      {/* Selected Image Preview & Action Button */}
      {previewUrl && (
        <div style={{
          marginTop: '24px',
          maxWidth: '600px',
          margin: '24px auto 0 auto',
          background: '#ffffff',
          border: '1px solid #e6dcce',
          borderRadius: '20px',
          padding: '16px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <img
              src={previewUrl}
              alt="Leaf Preview"
              style={{ width: '64px', height: '64px', borderRadius: '14px', objectFit: 'cover', border: '1px solid #e6dcce' }}
            />
            <div style={{ textAlign: 'left' }}>
              <p style={{ fontSize: '0.9rem', fontWeight: '700', color: '#3a3532' }}>Leaf Image Selected</p>
              <p style={{ fontSize: '0.78rem', color: '#7a8b75', fontWeight: '600' }}>Ready for AI Pathology & RAG Search</p>
            </div>
          </div>

          <button
            onClick={handleRunAnalysis}
            disabled={loading}
            className="btn-pill-primary"
          >
            <Sparkles size={18} />
            {loading ? 'Analyzing...' : 'Detect Disease & RAG'}
          </button>
        </div>
      )}

    </div>
  );
}

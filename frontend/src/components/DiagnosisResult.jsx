import React, { useState, useRef, useEffect } from 'react';
import { AlertOctagon, CheckCircle2, Cpu, FileText, Leaf, FlaskConical, Shield, Volume2, VolumeX, Play, Pause, Square, MessageSquare, ArrowRight } from 'lucide-react';

export default function DiagnosisResult({ result, selectedLanguage, onGoToAgroBot }) {
  const [playbackState, setPlaybackState] = useState('idle'); // 'idle', 'playing', 'paused'
  const [voiceSource, setVoiceSource] = useState(null);
  const [loadingAudio, setLoadingAudio] = useState(false);
  const audioRef = useRef(null);

  // Clean up audio on unmount or when result changes
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setPlaybackState('idle');
    };
  }, [result]);

  if (!result) return null;

  // Handle Smart Leaf Guard rejection
  if (!result.is_valid_leaf) {
    return (
      <div className="warm-card" style={{ borderLeft: '4px solid #c67d63' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
          <AlertOctagon size={28} color="#c67d63" />
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#c67d63' }}>Smart Leaf Guard Validation Alert</h3>
            <p style={{ fontSize: '0.85rem', color: '#827a74' }}>Chlorophyll & Vegetation Verification Failed</p>
          </div>
        </div>
        <p style={{ fontSize: '0.9rem', color: '#3a3532', marginBottom: '12px' }}>
          {result.error_message}
        </p>
        <div className="warm-card-sm">
          <strong style={{ fontSize: '0.85rem', color: '#c67d63' }}>Guidance for Farmers:</strong>
          <ul style={{ fontSize: '0.82rem', color: '#827a74', paddingLeft: '20px', marginTop: '6px' }}>
            <li>Upload a clear photograph focused directly on the crop leaf.</li>
            <li>Avoid non-plant objects (vehicles, faces, furniture, artificial tools).</li>
            <li>Ensure adequate natural lighting.</li>
          </ul>
        </div>
      </div>
    );
  }

  const { prediction, advisory } = result;
  const isHealthy = prediction.is_healthy;
  const badgeClass = isHealthy ? 'badge-healthy' : 'badge-disease';
  const badgeLabel = isHealthy ? 'HEALTHY CROP' : 'PATHOLOGY DETECTED';

  const handlePlayVoice = async () => {
    // If currently paused, resume immediately
    if (playbackState === 'paused' && audioRef.current) {
      audioRef.current.play();
      setPlaybackState('playing');
      return;
    }

    // Stop and reset any previously active audio element
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }

    let scriptText = result.selected_language_voice;
    if (!scriptText) {
      if (isHealthy) {
        scriptText = selectedLanguage === 'English'
          ? `Great news! Your ${prediction.crop || 'crop'} is completely healthy. No pesticide or chemical treatment is needed.`
          : `बधाई हो! आपकी ${prediction.crop || 'फसल'} पूरी तरह स्वस्थ और सुरक्षित है। किसी भी कीटनाशक या रासायनिक उपचार की आवश्यकता नहीं है।`;
      } else {
        scriptText = advisory.organic_treatment || "फसल के लिए अनुशंसित जैविक उपचार अपनाएं।";
      }
    }

    setLoadingAudio(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/inworld-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: scriptText, language: selectedLanguage })
      });
      const data = await res.json();
      
      if (data.has_audio && data.audio_url) {
        const audio = new Audio(`http://127.0.0.1:8000${data.audio_url}`);
        audioRef.current = audio;

        audio.onplay = () => {
          setPlaybackState('playing');
          setVoiceSource(data.source || 'Sarvam AI Neural Voice');
        };
        audio.onpause = () => {
          if (audio.currentTime > 0 && !audio.ended) {
            setPlaybackState('paused');
          } else {
            setPlaybackState('idle');
          }
        };
        audio.onended = () => {
          setPlaybackState('idle');
        };
        audio.onerror = (err) => {
          console.error("Audio playback error:", err);
          setPlaybackState('idle');
        };

        await audio.play();
      } else {
        alert("Sarvam voice engine returned no audio stream. Please ensure backend is running.");
      }
    } catch (e) {
      console.warn("Voice endpoint error:", e);
      alert("Voice engine offline. Please ensure FastAPI server is running on port 8000.");
    } finally {
      setLoadingAudio(false);
    }
  };

  const handlePauseVoice = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setPlaybackState('paused');
    }
  };

  const handleResumeVoice = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setPlaybackState('playing');
    }
  };

  const handleStopVoice = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setPlaybackState('idle');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Primary Diagnostic Summary Header */}
      <div className="warm-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '16px' }}>
          <div>
            <span className={`badge-pill ${badgeClass}`} style={{ marginBottom: '10px' }}>
              {badgeLabel}
            </span>
            <h2 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.8rem', fontWeight: '600', color: '#3a3532' }}>
              {prediction.display_title}
            </h2>
            <p style={{ fontSize: '0.9rem', color: '#827a74', marginTop: '6px' }}>
              <strong>Crop:</strong> {prediction.crop} &nbsp;|&nbsp; 
              <strong> Pathogen:</strong> {advisory.cause || 'Diagnostic Evaluation'} &nbsp;|&nbsp; 
              <strong> Severity:</strong> {advisory.severity || 'Moderate'}
            </p>
          </div>

          {/* Third-Party Neural Voice Controller Toolbar */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {playbackState === 'idle' && (
                <button
                  onClick={handlePlayVoice}
                  disabled={loadingAudio}
                  className="btn-pill-primary"
                  title="Play remedy voice"
                >
                  <Play size={16} />
                  {loadingAudio ? 'Loading Voice...' : (isHealthy ? `🔊 Announce Health (${selectedLanguage})` : `🔊 Play Voice Remedy (${selectedLanguage})`)}
                </button>
              )}

              {playbackState === 'playing' && (
                <>
                  <button
                    onClick={handlePauseVoice}
                    className="btn-pill-primary"
                    style={{ background: '#d97706' }}
                    title="Pause voice playback"
                  >
                    <Pause size={16} /> Pause Voice
                  </button>
                  <button
                    onClick={handleStopVoice}
                    className="btn-pill-primary"
                    style={{ background: '#dc2626' }}
                    title="Stop voice playback"
                  >
                    <Square size={16} /> Stop Voice
                  </button>
                </>
              )}

              {playbackState === 'paused' && (
                <>
                  <button
                    onClick={handleResumeVoice}
                    className="btn-pill-primary"
                    style={{ background: '#10b981' }}
                    title="Resume voice playback"
                  >
                    <Play size={16} /> Resume Voice
                  </button>
                  <button
                    onClick={handleStopVoice}
                    className="btn-pill-primary"
                    style={{ background: '#dc2626' }}
                    title="Stop voice playback"
                  >
                    <Square size={16} /> Stop Voice
                  </button>
                </>
              )}
            </div>

            {playbackState !== 'idle' && (
              <span style={{ fontSize: '0.78rem', color: playbackState === 'playing' ? '#10b981' : '#d97706', fontWeight: '700' }}>
                {playbackState === 'playing' ? '🔊 Playing Voice Narration...' : '⏸ Voice Playback Paused'}
              </span>
            )}
          </div>
        </div>

        {voiceSource && (
          <div style={{ fontSize: '0.78rem', color: '#7a8b75', fontWeight: '600', marginBottom: '10px' }}>
            Voice Engine: {voiceSource}
          </div>
        )}

        {/* Confidence Progress Bar */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', color: '#3a3532', fontWeight: '600' }}>
            <span>AI Pathology Confidence:</span>
            <span style={{ color: '#c67d63' }}>{prediction.confidence}%</span>
          </div>
          <div className="progress-container">
            <div className="progress-bar" style={{ width: `${prediction.confidence}%` }}></div>
          </div>
        </div>
      </div>

      {/* Grad-CAM Heatmap & Diagnostic Probabilities */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        
        {prediction.gradcam_overlay_b64 && (
          <div className="warm-card-sm">
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#c67d63', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Cpu size={16} /> Grad-CAM Visual Heatmap
            </h4>
            <img
              src={prediction.gradcam_overlay_b64}
              alt="Grad-CAM Visual Heatmap"
              style={{ width: '100%', height: '180px', objectFit: 'cover', borderRadius: '14px', border: '1px solid #e6dcce' }}
            />
            <p style={{ fontSize: '0.75rem', color: '#827a74', marginTop: '6px' }}>
              Highlights specific leaf lesions triggering classification.
            </p>
          </div>
        )}

        <div className="warm-card-sm">
          <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#7a8b75', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle2 size={16} /> Diagnostic Probabilities
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {prediction.top3_predictions && prediction.top3_predictions.map((top, idx) => (
              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', background: '#ffffff', border: '1px solid #e6dcce', padding: '8px 14px', borderRadius: '10px' }}>
                <span style={{ color: '#3a3532', fontWeight: '600' }}>{idx + 1}. {top.disease_display}</span>
                <span style={{ color: '#c67d63', fontWeight: '700' }}>{top.confidence}%</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Actionable Treatment & AgroBot CTA Link */}
      <div className="warm-card" style={{ borderLeft: '4px solid #7a8b75' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#3a3532', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} color="#7a8b75" />
            Agronomic Grounded Treatment Plan
          </h3>
          <span className="badge-tag">ICAR / CIBRC Standards</span>
        </div>

        <div style={{ background: '#f5efe6', border: '1px solid #e6dcce', borderRadius: '16px', padding: '18px', marginBottom: '20px' }}>
          <p style={{ fontSize: '0.92rem', color: '#3a3532', lineHeight: '1.6' }}>
            "{advisory.organic_treatment}"
          </p>
        </div>

        {/* Treatment Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', marginBottom: '24px' }}>
          
          <div className="warm-card-sm" style={{ borderTop: '3px solid #7a8b75' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: '#7a8b75', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Leaf size={16} /> Organic & Bio-Controls
            </h4>
            <p style={{ fontSize: '0.82rem', color: '#655e58', lineHeight: '1.4' }}>
              {advisory.organic_treatment}
            </p>
          </div>

          <div className="warm-card-sm" style={{ borderTop: '3px solid #c67d63' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: '#c67d63', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <FlaskConical size={16} /> Precision Chemical Dosage
            </h4>
            <p style={{ fontSize: '0.82rem', color: '#655e58', lineHeight: '1.4' }}>
              {advisory.chemical_treatment}
            </p>
          </div>

          <div className="warm-card-sm" style={{ borderTop: '3px solid #d9b48f' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: '#8c633a', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Shield size={16} /> Cultural Prevention
            </h4>
            <p style={{ fontSize: '0.82rem', color: '#655e58', lineHeight: '1.4' }}>
              {advisory.prevention}
            </p>
          </div>

        </div>

        {/* Prominent CTA to AgroBot */}
        <div style={{
          background: 'linear-gradient(135deg, #ffffff 0%, #f5efe6 100%)',
          border: '1px solid #e6dcce',
          borderRadius: '20px',
          padding: '20px',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#c67d63', fontWeight: '700', fontSize: '1.05rem' }}>
            <MessageSquare size={22} /> Want customized treatment steps or fertilizer calculations?
          </div>
          <p style={{ fontSize: '0.88rem', color: '#827a74', maxWidth: '560px' }}>
            Chat with AgroBot for personalized AI remedies, step-by-step pesticide preparation, and irrigation schedules.
          </p>
          <button
            onClick={() => onGoToAgroBot(prediction.display_title)}
            className="btn-pill-primary"
            style={{ padding: '12px 32px', fontSize: '0.95rem' }}
          >
            💬 Go to AgroBot for Personalized AI Remedies <ArrowRight size={18} />
          </button>
        </div>

      </div>

    </div>
  );
}

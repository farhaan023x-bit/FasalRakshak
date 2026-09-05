import React, { useState, useEffect, useRef } from 'react';
import { Volume2, VolumeX, Pause, Play, CheckCircle, X, Sparkles, AlertCircle } from 'lucide-react';

export default function AudioRemedyModal({ isOpen, onClose, diseaseResult, selectedLanguage, voiceScript }) {
  const [playbackState, setPlaybackState] = useState('idle'); // 'idle', 'playing', 'paused'
  const [loadingAudio, setLoadingAudio] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setPlaybackState('idle');
    }
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [isOpen]);

  if (!isOpen || !diseaseResult) return null;

  const handlePlayVoice = async () => {
    if (playbackState === 'paused' && audioRef.current) {
      audioRef.current.play();
      setPlaybackState('playing');
      return;
    }

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const isHealthy = diseaseResult.prediction?.is_healthy;
    let textToSpeak = voiceScript || diseaseResult.selected_language_voice;
    if (!textToSpeak) {
      if (isHealthy) {
        textToSpeak = selectedLanguage === 'English'
          ? "Great news! Your crop is completely healthy and vigorous. No pesticide or chemical treatment is needed."
          : "बधाई हो! आपकी फसल पूरी तरह स्वस्थ और सुरक्षित है। किसी भी कीटनाशक या रासायनिक उपचार की आवश्यकता नहीं है।";
      } else {
        textToSpeak = diseaseResult.advisory?.organic_treatment || "रोग का उपचार अपनाएं।";
      }
    }

    setLoadingAudio(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/inworld-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToSpeak, language: selectedLanguage })
      });
      const data = await res.json();
      if (data.has_audio && data.audio_url) {
        const audio = new Audio(`http://127.0.0.1:8000${data.audio_url}`);
        audioRef.current = audio;
        audio.onplay = () => setPlaybackState('playing');
        audio.onpause = () => {
          if (audio.currentTime > 0 && !audio.ended) setPlaybackState('paused');
          else setPlaybackState('idle');
        };
        audio.onended = () => setPlaybackState('idle');
        audio.onerror = () => setPlaybackState('idle');
        await audio.play();
      }
    } catch (e) {
      console.warn("Audio modal voice error:", e);
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

  const handleStopVoice = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setPlaybackState('idle');
  };

  const handleDecline = () => {
    handleStopVoice();
    onClose();
  };

  const displayTitle = diseaseResult.prediction?.display_title || "Crop Disease Detected";
  const organicAdvisory = diseaseResult.advisory?.organic_treatment || "Apply 5% Neem Seed Kernel Extract.";

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              background: 'rgba(16, 185, 129, 0.2)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              padding: '10px',
              borderRadius: '12px',
              color: '#10b981'
            }}>
              <Volume2 size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#fff' }}>
                🔊 Hear Remedy Announcement?
              </h3>
              <p style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                Real-Time Voice Assistant in <strong>{selectedLanguage}</strong>
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#9ca3af', cursor: 'pointer', padding: '4px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Diagnostic Banner */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.05)',
          borderLeft: '4px solid #10b981',
          padding: '14px',
          borderRadius: '10px',
          marginBottom: '20px'
        }}>
          <h4 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#34d399', marginBottom: '4px' }}>
            {displayTitle}
          </h4>
          <p style={{ fontSize: '0.85rem', color: '#d1d5db', lineHeight: '1.4' }}>
            {organicAdvisory}
          </p>
        </div>

        {/* Prompt Body */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <p style={{ fontSize: '0.95rem', color: '#e5e7eb', marginBottom: '8px' }}>
            "Would you like FasalRakshak AI to speak aloud the complete remedy in <strong>{selectedLanguage}</strong>?"
          </p>
          <span className="badge-tag">Sarvam AI Regional Neural Voice</span>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {playbackState === 'playing' ? (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handlePauseVoice}
                className="btn-secondary"
                style={{ flex: 1, justifyContent: 'center', background: 'rgba(245, 158, 11, 0.2)', borderColor: 'rgba(245, 158, 11, 0.4)', color: '#fbbf24' }}
              >
                <Pause size={18} />
                Pause Voice
              </button>
              <button
                onClick={handleStopVoice}
                className="btn-secondary"
                style={{ flex: 1, justifyContent: 'center', background: 'rgba(239, 68, 68, 0.2)', borderColor: 'rgba(239, 68, 68, 0.4)', color: '#f87171' }}
              >
                <VolumeX size={18} />
                Stop Voice
              </button>
            </div>
          ) : playbackState === 'paused' ? (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={handlePlayVoice}
                className="btn-primary"
                style={{ flex: 1, justifyContent: 'center' }}
              >
                <Play size={18} />
                Resume Voice
              </button>
              <button
                onClick={handleStopVoice}
                className="btn-secondary"
                style={{ flex: 1, justifyContent: 'center', background: 'rgba(239, 68, 68, 0.2)', borderColor: 'rgba(239, 68, 68, 0.4)', color: '#f87171' }}
              >
                <VolumeX size={18} />
                Stop Voice
              </button>
            </div>
          ) : (
            <button
              onClick={handlePlayVoice}
              disabled={loadingAudio}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
            >
              <Volume2 size={18} />
              {loadingAudio ? 'Loading Voice...' : `🔊 Yes, Announce Voice Remedy Now`}
            </button>
          )}

          <button
            onClick={handleDecline}
            className="btn-secondary"
            style={{ width: '100%', justifyContent: 'center' }}
          >
            <X size={16} />
            No, I Will Read Text
          </button>
        </div>

      </div>
    </div>
  );
}

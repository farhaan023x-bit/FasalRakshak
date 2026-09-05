import React, { useState, useEffect } from 'react';
import WeatherBanner from './components/WeatherBanner';
import Navbar from './components/Navbar';
import Home from './components/Home';
import ImageUploadSection from './components/ImageUploadSection';
import DiagnosisResult from './components/DiagnosisResult';
import AgroBot from './components/AgroBot';
import About from './components/About';
import SdgImpact from './components/SdgImpact';

export default function App() {
  const [activeTab, setActiveTab] = useState('home'); // 'home', 'detection', 'agrobot', 'about', 'sdg'
  const [location, setLocation] = useState('Ranchi, Jharkhand');
  const [selectedLang, setSelectedLang] = useState('Hindi');
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUploadedFile, setLastUploadedFile] = useState(null);
  const [activeDiseaseContext, setActiveDiseaseContext] = useState(null);

  // Automatically re-fetch advisory in newly selected language if a file has been diagnosed
  useEffect(() => {
    if (lastUploadedFile && activeTab === 'detection') {
      handleAnalyzeImage({ type: 'file', payload: lastUploadedFile });
    }
  }, [selectedLang]);

  const handleAnalyzeImage = async ({ type, payload }) => {
    setLoading(true);
    if (type === 'file') {
      setLastUploadedFile(payload);
    }

    try {
      const formData = new FormData();
      formData.append('language', selectedLang);

      if (type === 'file') {
        formData.append('file', payload);
      }

      const res = await fetch('http://127.0.0.1:8000/api/predict', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      setDiagnosisResult(data);

      if (data.is_valid_leaf && data.prediction) {
        setActiveDiseaseContext(data.prediction.display_title);
      }
    } catch (err) {
      console.error("Inference Error:", err);
      alert("Failed to analyze crop leaf image. Please ensure the FastAPI backend is running on http://127.0.0.1:8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoToAgroBot = (diseaseTitle) => {
    setActiveDiseaseContext(diseaseTitle);
    setActiveTab('agrobot');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg-beige)' }}>
      
      {/* 1. Real-Time Top Weather Ticker Banner */}
      <WeatherBanner location={location} onLocationChange={setLocation} />

      {/* 2. Aesthetic Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        selectedLang={selectedLang}
        setSelectedLang={setSelectedLang}
      />

      {/* 3. Main Workspace */}
      <main style={{ flex: 1, maxWidth: '1200px', width: '100%', margin: '0 auto', padding: '32px 24px' }}>
        
        {activeTab === 'home' && (
          <Home onNavigate={(tab) => setActiveTab(tab)} />
        )}

        {activeTab === 'detection' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            <ImageUploadSection onAnalyze={handleAnalyzeImage} loading={loading} />
            <DiagnosisResult
              result={diagnosisResult}
              selectedLanguage={selectedLang}
              onGoToAgroBot={handleGoToAgroBot}
            />
          </div>
        )}

        {activeTab === 'agrobot' && (
          <AgroBot
            activeContext={activeDiseaseContext}
            selectedLanguage={selectedLang}
          />
        )}

        {activeTab === 'about' && (
          <About />
        )}

        {activeTab === 'sdg' && (
          <SdgImpact />
        )}

      </main>

      {/* Clean Footer */}
      <footer style={{ borderTop: '1px solid #e6dcce', padding: '24px', textAlign: 'center', fontSize: '0.82rem', color: '#827a74', background: '#f5efe6' }}>
        <strong>FasalRakshak AI</strong> &bull; Precision AI Agriculture & Micro-Climate Advisory Platform
      </footer>

    </div>
  );
}

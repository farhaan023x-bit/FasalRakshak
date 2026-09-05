import React, { useState, useEffect } from 'react';
import { CloudRain, Wind, Thermometer, Droplets, ShieldCheck, AlertTriangle, MapPin } from 'lucide-react';

export default function WeatherBanner({ location, onLocationChange }) {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWeather(location);
  }, [location]);

  const fetchWeather = async (loc) => {
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/weather?location=${encodeURIComponent(loc)}`);
      const data = await response.json();
      setWeatherData(data);
    } catch (err) {
      console.error("Failed to fetch weather:", err);
      setWeatherData({
        location: loc,
        temperature: 28.5,
        humidity: 82,
        wind_speed: 9.4,
        rain_probability: 65,
        spray_badge_text: "⛔ DO NOT SPRAY TODAY (Rain Forecast)",
        spray_badge_color: "#c67d63",
        available_districts: ["Ranchi, Jharkhand", "Patna, Bihar", "Ludhiana, Punjab", "Nashik, Maharashtra", "Guntur, Andhra Pradesh", "Jaipur, Rajasthan", "Varanasi, Uttar Pradesh", "Kolkata, West Bengal", "Bhopal, Madhya Pradesh", "Bengaluru, Karnataka"]
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading || !weatherData) {
    return (
      <div style={{ background: '#f5efe6', borderBottom: '1px solid #e6dcce', padding: '10px 24px', textAlign: 'center', color: '#827a74', fontSize: '0.88rem' }}>
        <span>🌦️ Loading real-time micro-climate advisory...</span>
      </div>
    );
  }

  return (
    <div style={{ background: '#f5efe6', borderBottom: '1px solid #e6dcce', padding: '12px 32px' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
        
        {/* District & Climate Metrics */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={18} color="#c67d63" />
            <select
              value={location}
              onChange={(e) => onLocationChange(e.target.value)}
              style={{
                background: '#ffffff',
                color: '#3a3532',
                border: '1px solid #e6dcce',
                borderRadius: '50px',
                padding: '4px 14px',
                fontSize: '0.88rem',
                fontWeight: '600',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              {weatherData.available_districts.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '18px', fontSize: '0.88rem', color: '#3a3532' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Thermometer size={16} color="#c67d63" />
              <strong>{weatherData.temperature}°C</strong>
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Droplets size={16} color="#7a8b75" />
              <strong>{weatherData.humidity}%</strong> Humidity
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CloudRain size={16} color="#8c633a" />
              <strong>{weatherData.rain_probability}%</strong> Rain Chance
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Wind size={16} color="#7a8b75" />
              <strong>{weatherData.wind_speed} km/h</strong> Wind
            </span>
          </div>
        </div>

        {/* Dynamic Farmer Spray Warning Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: '#ffffff',
          border: '1px solid #e6dcce',
          padding: '6px 18px',
          borderRadius: '50px',
          boxShadow: '0 2px 10px rgba(180, 150, 120, 0.08)'
        }}>
          {weatherData.spray_status === 'SAFE_TO_SPRAY' ? (
            <ShieldCheck size={18} color="#7a8b75" />
          ) : (
            <AlertTriangle size={18} color="#c67d63" />
          )}
          <span style={{ color: '#3a3532', fontWeight: '700', fontSize: '0.85rem' }}>
            {weatherData.spray_badge_text}
          </span>
        </div>

      </div>
    </div>
  );
}

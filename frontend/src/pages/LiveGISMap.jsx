import { MapPin, Search, Filter, Flame, AlertTriangle, Clock, ThermometerSun, Navigation, Info, Zap, Wind, Droplets, Brain, AlertOctagon, ShieldAlert, Target, Activity } from "lucide-react";
import { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { fetchFireLocations, fetchRawFireLocations, checkBackendHealth, getFireInsights, classifyFireLocal } from '../services/fireApi';

// Fix leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// ================= Fire Type Icons ==================
const createFireIcon = (emoji, color, intensity = "Moderate", windDegree = 0) => {
  const intensityColors = {
    "Low":      "#22C55E",
    "Moderate": "#EAB308",
    "High":     "#F97316",
    "Extreme":  "#DC2626",
  };
  const intColor = intensityColors[intensity] || color;
  // Spreading direction is opposite of wind origin (wind_degree + 180)
  const spreadDegree = (windDegree + 180) % 360;

  return L.divIcon({
  className: 'classified-fire-marker',
  html: `
    <div style="position:relative; width:30px; height:30px;">
      <!-- Spreading Direction Arrow -->
      <div style="
        position:absolute;
        top:-15px; left:50%;
        width:2px; height:15px;
        background:${intColor};
        transform-origin: bottom center;
        transform: translateX(-50%) rotate(${spreadDegree}deg);
        z-index: 10;
        opacity: 0.9;
      ">
        <div style="
          position:absolute;
          top:-4px; left:-4px;
          width: 0; height: 0;
          border-left: 5px solid transparent;
          border-right: 5px solid transparent;
          border-bottom: 8px solid ${intColor};
        "></div>
      </div>
      
      <!-- Main Marker -->
      <div style="
        width:30px;
        height:30px;
        border-radius:50%;
        background:${color};
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:15px;
        border:2px solid ${intColor};
        box-shadow:0 0 14px ${intColor};
        position:relative;
        z-index: 20;
      ">
        ${emoji}
        <span style="
          position:absolute;
          inset:-4px;
          border-radius:50%;
          border:2px solid ${intColor};
          animation: classifiedPulse 2s infinite;
        "></span>
      </div>
    </div>
    <style>
      @keyframes classifiedPulse{
        0%{transform:scale(.8);opacity:.8;}
        70%{transform:scale(1.6);opacity:0;}
        100%{transform:scale(1.6);opacity:0;}
      }
    </style>
  `,
  iconSize: [30, 45],
  iconAnchor: [15, 30],
  popupAnchor: [0, -30],
});
};

// Fire type → icon mapping (matching the backend classification agent)
const FIRE_TYPE_CONFIG = {
  "Industrial Fire":    { emoji: "🏭", color: "#EF4444", label: "Industrial" },
  "Commercial Fire":    { emoji: "🏢", color: "#8B5CF6", label: "Commercial" },
  "Forest Fire":        { emoji: "🌲", color: "#22C55E", label: "Forest" },
  "Agricultural Fire":  { emoji: "🌾", color: "#EAB308", label: "Agricultural" },
  "Residential Fire":   { emoji: "🏠", color: "#EC4899", label: "Residential" },
};

// Pre-create icons (Fallback for missing data)
const DEFAULT_ICON = createFireIcon("🔥", "#F97316", "Moderate", 0);

// Intensity badge colors
const intensityColors = {
  "Low":      "#22C55E",
  "Moderate": "#EAB308",
  "High":     "#F97316",
  "Extreme":  "#DC2626",
};



export default function LiveGISMap() {
  const [firmsData, setFirmsData] = useState([]);
  const [selectedFire, setSelectedFire] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [backendOnline, setBackendOnline] = useState(false);
  const [error, setError] = useState(null);

  // Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('All Types');
  const [intensityFilter, setIntensityFilter] = useState('All Intensity');
  const [countryFilter, setCountryFilter] = useState('All Countries');

  useEffect(() => {
    loadFromBackend();
  }, []);

  const loadFromBackend = async () => {
    setIsLoading(true);
    setError(null);

    // Check backend health first
    const healthy = await checkBackendHealth();
    setBackendOnline(healthy);

    if (!healthy) {
      setError("Backend server is offline. Start the FastAPI server: uvicorn api:app --reload --port 8000");
      setIsLoading(false);
      return;
    }

    try {
      // Fetch RAW fires from the dataset directly
      const fires = await fetchRawFireLocations();
      if (fires.length > 0) {
        setFirmsData(fires);
        setSelectedFire(fires[0]);
      } else {
        setError("No classified fire data available. Run the classification agent first.");
      }
    } catch (err) {
      console.error("Backend API Error:", err);
      setError("Failed to fetch fire data from backend.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFastClassify = async () => {
    setIsLoading(true);
    try {
      // Fetch fires classified by the AI classification agent
      const classified = await fetchFireLocations();
      if (classified.length > 0) {
        setFirmsData(classified);
        setSelectedFire(classified[0]);
      } else {
        setError("No classified fire data available. Run the classification agent first.");
      }
    } catch (err) {
      console.error("Classification fetch error:", err);
      setError("Failed to fetch classified fire data.");
    } finally {
      setIsLoading(false);
    }
  };

  // Extract unique values for filters (safely handle missing properties on raw fires)
  const uniqueCountries = [...new Set(firmsData.map(f => f.country || "Unknown"))].filter(Boolean);
  const uniqueTypes = [...new Set(firmsData.map(f => f.fire_type || "Unclassified"))].filter(Boolean);

  // Apply Filters
  const filteredData = firmsData.filter(fire => {
    const matchesSearch = !searchQuery ||
      (fire.city || 'Unknown').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (fire.country || 'Unknown').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (fire.fire_type || 'Unclassified').toLowerCase().includes(searchQuery.toLowerCase());

    const matchesType = typeFilter === 'All Types' || (fire.fire_type || 'Unclassified') === typeFilter;
    const matchesIntensity = intensityFilter === 'All Intensity' || (fire.intensity || 'Low') === intensityFilter;
    const matchesCountry = countryFilter === 'All Countries' || (fire.country || 'Unknown') === countryFilter;

    return matchesSearch && matchesType && matchesIntensity && matchesCountry;
  });

  // Fire type distribution
  const typeDistribution = {};
  firmsData.forEach(f => {
    const t = f.fire_type || "Unknown";
    typeDistribution[t] = (typeDistribution[t] || 0) + 1;
  });

  const handleReset = () => {
    setSearchQuery('');
    setTypeFilter('All Types');
    setIntensityFilter('All Intensity');
    setCountryFilter('All Countries');
  };

  return (
    <div style={{ maxWidth: '1400px', width: '100%', margin: '0 auto', paddingBottom: '2rem' }}>

      {/* ================= Header ================= */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '2.5rem', margin: '0 0 0.5rem 0', color: '#f8fafc', letterSpacing: '-0.5px' }}>Live GIS Map</h2>
          <p style={{ color: '#a1a1aa', margin: 0, fontSize: '1.1rem' }}>
            AI-classified fire hotspots from the Geoapify + Groq classification agent.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          {Object.entries(typeDistribution).map(([type, count]) => {
            const config = FIRE_TYPE_CONFIG[type];
            return (
              <div key={type} style={{
                backgroundColor: `${config ? config.color : '#64748b'}15`,
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                border: `1px solid ${config ? config.color : '#64748b'}40`,
                color: config ? config.color : '#94a3b8',
                fontSize: '0.9rem',
              }}>
                <span style={{ fontWeight: 'bold' }}>{count}</span> {config ? config.label : type}
              </div>
            );
          })}
        </div>
      </div>

      {/* ================= Filters ================= */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
        <div style={{ flex: 1, minWidth: '200px', backgroundColor: 'rgba(15,15,15,0.6)', border: '1px solid #1e293b', borderRadius: '8px', padding: '0.75rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Search size={18} color="#71717a" />
          <input
            placeholder="Search city, country, or fire type..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: '#f4f4f5', width: '100%', outline: 'none' }}
          />
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          style={{ backgroundColor: 'rgba(15,15,15,0.6)', color: '#f4f4f5', border: '1px solid #1e293b', padding: '0.75rem 1rem', borderRadius: '8px', outline: 'none' }}
        >
          <option>All Types</option>
          <option>Industrial Fire</option>
          <option>Commercial Fire</option>
          <option>Forest Fire</option>
          <option>Agricultural Fire</option>
          <option>Residential Fire</option>
        </select>

        <select
          value={intensityFilter}
          onChange={(e) => setIntensityFilter(e.target.value)}
          style={{ backgroundColor: 'rgba(15,15,15,0.6)', color: '#f4f4f5', border: '1px solid #1e293b', padding: '0.75rem 1rem', borderRadius: '8px', outline: 'none' }}
        >
          <option>All Intensity</option>
          <option>Low</option>
          <option>Moderate</option>
          <option>High</option>
          <option>Extreme</option>
        </select>

        {uniqueCountries.length > 1 && (
          <select
            value={countryFilter}
            onChange={(e) => setCountryFilter(e.target.value)}
            style={{ backgroundColor: 'rgba(15,15,15,0.6)', color: '#f4f4f5', border: '1px solid #1e293b', padding: '0.75rem 1rem', borderRadius: '8px', outline: 'none' }}
          >
            <option>All Countries</option>
            {uniqueCountries.map(c => <option key={c}>{c}</option>)}
          </select>
        )}

        <button
          onClick={handleReset}
          style={{ backgroundColor: 'rgba(255,255,255,0.1)', color: '#f4f4f5', border: '1px solid #1e293b', padding: '0.75rem 1rem', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Filter size={16} /> Clear
        </button>

        <button
          onClick={loadFromBackend}
          style={{ backgroundColor: 'rgba(59,130,246,0.15)', color: '#93c5fd', border: '1px solid rgba(59,130,246,0.3)', padding: '0.75rem 1rem', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <Zap size={16} /> Refresh
        </button>
      </div>

      {/* ================= Backend Status ================= */}
      {backendOnline ? (
        <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#6ee7b7', fontSize: '0.95rem' }}>
          <Info size={18} />
          <strong>Backend Connected</strong> — Showing {filteredData.length} of {firmsData.length} AI-classified hotspots
        </div>
      ) : (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fca5a5', fontSize: '0.95rem' }}>
          <AlertTriangle size={18} />
          <strong>Backend Offline</strong> — {error || "Start the FastAPI server to load classified data."}
        </div>
      )}

      {/* ================= Main Grid ================= */}
      <div className="gis-main-grid">

        {/* ================= Map ================= */}
        <div className="thermal-card" style={{ height: '700px', padding: 0, overflow: 'hidden', position: 'relative', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '1.5rem', borderBottom: '1px solid #1e293b', backgroundColor: 'rgba(2, 6, 23, 0.4)', zIndex: 1000, position: 'relative' }}>
            <h3 style={{ margin: 0, color: '#e4e4e7', fontSize: '1.2rem', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Navigation size={20} /> AI Fire Classification Map
            </h3>
          </div>

          <div style={{ flex: 1, backgroundColor: '#09090b', zIndex: 1, position: 'relative' }}>
            {isLoading && (
              <div style={{ position: 'absolute', inset: 0, background: 'rgba(2,6,23,.85)', color: '#E2E8F0', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 999, fontSize: '1.1rem' }}>
                Loading classified fire hotspots...
              </div>
            )}

            {/* Classify Button (Top Right Absolute) */}
            <div style={{ position: 'absolute', top: 20, right: 20, zIndex: 1000, display: 'flex', gap: '1rem' }}>
              <button 
                onClick={handleFastClassify}
                style={{ 
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', 
                  color: '#fff', 
                  border: 'none', 
                  padding: '12px 24px', 
                  borderRadius: '8px', 
                  cursor: 'pointer',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 15px rgba(59, 130, 246, 0.4)',
                  transition: 'all 0.2s ease'
                }}
                onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <Brain size={18} />
                Run Classification Agent
              </button>
            </div>

            <MapContainer center={[22, 85]} zoom={4} style={{ height: '100%', width: '100%', backgroundColor: '#020617' }}>
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {filteredData.map(fire => {
                const isRaw = !fire.fire_type || fire.fire_type === "Unknown";
                const config = FIRE_TYPE_CONFIG[fire.fire_type];
                const icon = isRaw 
                  ? L.divIcon({ className: 'custom-fire-marker', html: `<div style="width:14px; height:14px; background:#ef4444; border-radius:50%;"></div>`, iconSize: [14, 14] })
                  : createFireIcon(config?.emoji || "🔥", config?.color || "#F97316", fire.intensity, fire.wind_degree || 0);

                return (
                  <Marker
                    key={fire.id}
                    position={[fire.latitude, fire.longitude]}
                    icon={icon}
                    eventHandlers={{ click: () => setSelectedFire(fire) }}
                  >
                    <Popup minWidth={280}>
                      <div style={{ fontFamily: 'Inter, sans-serif' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                          <Flame color={config?.color || '#F97316'} size={18} />
                          <h3 style={{ margin: 0, color: '#111827', fontSize: '1rem' }}>{fire.fire_type || "Unclassified Hotspot"}</h3>
                        </div>

                        <p style={{ margin: '4px 0', color: '#475569', fontSize: '0.85rem' }}>
                          📍 {fire.city ? <><strong>{fire.city}</strong>, {fire.country}</> : <>{Number(fire.latitude).toFixed(4)}°, {Number(fire.longitude).toFixed(4)}°</>}
                        </p>

                        {/* Raw sensor data (always available) */}
                        <div style={{ fontSize: '.78rem', color: '#64748B', marginTop: 4 }}>
                          🛰 {fire.satellite || 'N/A'} &nbsp;|&nbsp; 🔥 FRP: {fire.frp} MW &nbsp;|&nbsp; 🌡 {fire.bright_ti4}K
                        </div>

                        {fire.intensity && (
                          <div style={{
                            display: 'inline-block', marginTop: 6, marginBottom: 8, marginRight: 8,
                            padding: '4px 10px', borderRadius: 999,
                            background: (intensityColors[fire.intensity] || '#64748B') + '22',
                            color: intensityColors[fire.intensity] || '#475569',
                            fontWeight: 700, fontSize: '.78rem',
                          }}>
                            🔥 {fire.intensity}
                          </div>
                        )}

                        {/* Insights only show if classified */}
                        {fire.fire_type && fire.fire_type !== "Unknown" && (
                          <div style={{ background: '#F8FAFC', borderRadius: 8, padding: 10, marginTop: 10 }}>
                            <div style={{ fontSize: '.78rem', fontWeight: 700, color: '#2563EB', marginBottom: 5 }}>
                              🧠 AI Reasoning & Insights
                            </div>
                            <p style={{ margin: 0, color: '#334155', fontSize: '.75rem', lineHeight: 1.5 }}>
                              <strong>Prediction:</strong> {getFireInsights(fire).prediction}
                            </p>
                            <p style={{ margin: '4px 0 0 0', color: '#334155', fontSize: '.75rem', lineHeight: 1.5 }}>
                              <strong>Cause:</strong> {getFireInsights(fire).causes}
                            </p>
                          </div>
                        )}
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </MapContainer>

            {/* ================= Legend ================= */}
            <div style={{
              position: 'absolute', bottom: 15, left: 15,
              background: 'rgba(15,23,42,.92)',
              backdropFilter: 'blur(8px)',
              padding: '14px 16px',
              borderRadius: 12,
              color: '#F8FAFC',
              zIndex: 999,
              border: '1px solid #334155',
              minWidth: 170,
            }}>
              <div style={{ fontWeight: 600, marginBottom: 10, fontSize: '0.85rem' }}>Fire Types</div>
              {Object.entries(FIRE_TYPE_CONFIG).map(([type, config]) => (
                <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
                  <div style={{
                    width: 18, height: 18, borderRadius: '50%',
                    background: config.color,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 10,
                  }}>{config.emoji}</div>
                  <span style={{ fontSize: '.78rem' }}>{type}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ================= Details Panel ================= */}
        <div className="thermal-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxHeight: '700px', overflowY: 'auto' }}>
          {selectedFire ? (
            <>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '1rem' }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1.5rem', color: '#f8fafc' }}>
                    {selectedFire.city || 'Unknown Location'}
                  </h3>
                  <p style={{ margin: '0.25rem 0 0 0', color: '#a1a1aa' }}>{selectedFire.country || 'Unknown Country'}</p>
                </div>
                <div style={{
                  backgroundColor: `${FIRE_TYPE_CONFIG[selectedFire.fire_type]?.color || '#F97316'}20`,
                  padding: '0.75rem',
                  borderRadius: '12px',
                  color: FIRE_TYPE_CONFIG[selectedFire.fire_type]?.color || '#F97316',
                  fontSize: '1.5rem',
                }}>
                  {FIRE_TYPE_CONFIG[selectedFire.fire_type]?.emoji || '🔥'}
                </div>
              </div>

              {/* Fire Type Badge */}
              {selectedFire.fire_type && selectedFire.fire_type !== "Unknown" && (
                <div style={{
                  backgroundColor: `${FIRE_TYPE_CONFIG[selectedFire.fire_type]?.color || '#F97316'}18`,
                  border: `1px solid ${FIRE_TYPE_CONFIG[selectedFire.fire_type]?.color || '#F97316'}50`,
                  padding: '0.5rem 1rem', borderRadius: '6px',
                  color: FIRE_TYPE_CONFIG[selectedFire.fire_type]?.color || '#F97316',
                  fontWeight: '700', display: 'inline-block', width: 'fit-content',
                  fontSize: '0.9rem', letterSpacing: '0.5px', textTransform: 'uppercase'
                }}>
                  {selectedFire.fire_type}
                </div>
              )}

              {/* Intensity Badge */}
              {selectedFire.intensity && (
                <div style={{
                  backgroundColor: `${intensityColors[selectedFire.intensity] || '#64748b'}18`,
                  border: `1px solid ${intensityColors[selectedFire.intensity] || '#64748b'}50`,
                  padding: '0.5rem 1rem', borderRadius: '6px',
                  color: intensityColors[selectedFire.intensity] || '#94a3b8',
                  fontWeight: '700', display: 'inline-block', width: 'fit-content',
                  fontSize: '0.85rem',
                }}>
                  ⚡ {selectedFire.intensity} Intensity
                </div>
              )}

              {/* Details Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1.5rem' }}>
                <div>
                  <p style={{ margin: '0 0 0.5rem 0', color: '#71717a', fontSize: '0.85rem' }}>Brightness</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc', fontSize: '1.2rem', fontWeight: '600' }}>
                    <ThermometerSun size={18} color={FIRE_TYPE_CONFIG[selectedFire.fire_type]?.color || '#F97316'} /> {selectedFire.brightness}K
                  </div>
                </div>
                <div>
                  <p style={{ margin: '0 0 0.5rem 0', color: '#71717a', fontSize: '0.85rem' }}>FRP</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc', fontSize: '1.2rem', fontWeight: '600' }}>
                    <Flame size={18} color="#EF4444" /> {selectedFire.frp} MW
                  </div>
                </div>
                <div>
                  <p style={{ margin: '0 0 0.5rem 0', color: '#71717a', fontSize: '0.85rem' }}>Coordinates</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc', fontSize: '1rem', fontWeight: '600' }}>
                    <MapPin size={18} color="#3b82f6" /> {Number(selectedFire.latitude).toFixed(4)}°, {Number(selectedFire.longitude).toFixed(4)}°
                  </div>
                </div>
                <div>
                  <p style={{ margin: '0 0 0.5rem 0', color: '#71717a', fontSize: '0.85rem' }}>Confidence</p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f8fafc', fontSize: '1.2rem', fontWeight: '600' }}>
                    {selectedFire.confidence}%
                  </div>
                </div>
              </div>

              {/* Weather Info */}
              {(selectedFire.temperature || selectedFire.wind_speed || selectedFire.humidity) && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem' }}>
                  <div>
                    <p style={{ margin: '0 0 0.3rem 0', color: '#71717a', fontSize: '0.8rem' }}>Temp</p>
                    <div style={{ color: '#f8fafc', fontWeight: '600', fontSize: '1rem' }}>
                      <ThermometerSun size={14} color="#F97316" /> {selectedFire.temperature}°C
                    </div>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 0.3rem 0', color: '#71717a', fontSize: '0.8rem' }}>Wind</p>
                    <div style={{ color: '#f8fafc', fontWeight: '600', fontSize: '1rem' }}>
                      <Wind size={14} color="#3b82f6" /> {selectedFire.wind_speed} km/h
                    </div>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 0.3rem 0', color: '#71717a', fontSize: '0.8rem' }}>Humidity</p>
                    <div style={{ color: '#f8fafc', fontWeight: '600', fontSize: '1rem' }}>
                      <Droplets size={14} color="#22D3EE" /> {selectedFire.humidity}%
                    </div>
                  </div>
                </div>
              )}

              {/* AI Reasoning (shown for all fires) */}
              <div style={{ backgroundColor: 'rgba(37, 99, 235, 0.08)', border: '1px solid rgba(37, 99, 235, 0.25)', padding: '1rem', borderRadius: '8px', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <Brain size={20} color="#3b82f6" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <p style={{ margin: 0, color: '#93c5fd', fontSize: '0.85rem', fontWeight: '700' }}>
                    AI Reasoning
                  </p>
                  <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.85rem', lineHeight: '1.6' }}>
                    {selectedFire.reasoning || 'No reasoning available for this hotspot. Click "Fast Classify Hotspots" to generate insights.'}
                  </p>
                </div>
              </div>

              {/* Satellite Info */}
              <div style={{ backgroundColor: 'rgba(249, 115, 22, 0.08)', border: '1px solid rgba(249, 115, 22, 0.25)', padding: '1rem', borderRadius: '8px', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <AlertTriangle size={20} color="#f97316" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <p style={{ margin: 0, color: '#fdba74', fontSize: '0.85rem', lineHeight: '1.5' }}>
                    <strong>Satellite:</strong> {selectedFire.satellite} &nbsp;|&nbsp; <strong>Date:</strong> {selectedFire.acq_date} &nbsp;|&nbsp; <strong>Time:</strong> {selectedFire.acq_time}
                  </p>
                  <p style={{ margin: 0, color: '#fdba74', fontSize: '0.85rem', lineHeight: '1.5' }}>
                    <strong>Day/Night:</strong> {selectedFire.daynight === 'D' ? 'Daytime' : 'Nighttime'} &nbsp;|&nbsp; <strong>Landuse:</strong> {selectedFire.landuse || 'Unknown'}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <button style={{ backgroundColor: '#3b82f6', color: '#ffffff', border: 'none', padding: '1rem', borderRadius: '8px', fontWeight: '600', fontSize: '1rem', cursor: 'pointer', transition: 'background-color 0.2s' }}
                  onMouseOver={e => e.currentTarget.style.backgroundColor = '#2563eb'}
                  onMouseOut={e => e.currentTarget.style.backgroundColor = '#3b82f6'}
                >
                  Generate Incident Report
                </button>
                <button style={{ backgroundColor: 'transparent', color: '#a1a1aa', border: '1px solid #1e293b', padding: '1rem', borderRadius: '8px', fontWeight: '600', fontSize: '1rem', cursor: 'pointer', transition: 'background-color 0.2s' }}
                  onMouseOver={e => e.currentTarget.style.backgroundColor = 'rgba(59,130,246,0.1)'}
                  onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  View Historical Data
                </button>
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#71717a', textAlign: 'center', padding: '2rem' }}>
              <MapPin size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#a1a1aa' }}>
                {isLoading ? 'Loading...' : 'Select a Hotspot'}
              </h3>
              <p style={{ margin: 0, fontSize: '0.9rem' }}>
                {isLoading ? 'Fetching classified fire data from backend...' : 'Click on a fire marker on the map to view AI classification details.'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

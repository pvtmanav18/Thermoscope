// import { Maximize2, Map } from 'lucide-react';
// import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
// import L from 'leaflet';
// import { useNavigate } from 'react-router-dom';

// // Create a realistic HTML icon for the dashboard map
// const createMiniIcon = (color) => L.divIcon({
//   className: 'custom-fire-marker',
//   html: `<div style="width: 14px; height: 14px; background-color: ${color}; border-radius: 50%; box-shadow: 0 0 10px 2px ${color}80; position: relative;">
//           <div style="position: absolute; top: 50%; left: 50%; width: 100%; height: 100%; background-color: ${color}; border-radius: 50%; transform: translate(-50%, -50%); animation: ping-marker 2s cubic-bezier(0, 0, 0.2, 1) infinite; opacity: 0.8;"></div>
//          </div>`,
//   iconSize: [14, 14],
//   iconAnchor: [7, 7],
// });

// const redMini = createMiniIcon('#3b82f6');
// const orangeMini = createMiniIcon('#f97316');

// export default function MapMockup() {
//   const navigate = useNavigate();
//   // Realistic dense area for street-level view (e.g. San Francisco or industrial zone)
//   const centerPos = [37.7749, -122.4194]; 

//   return (
//     <div className="thermal-card" style={{ height: '450px', padding: 0, overflow: 'hidden', position: 'relative', display: 'flex', flexDirection: 'column' }}>
      
//       {/* Header */}
//       <div style={{ padding: '1.25rem', borderBottom: '1px solid #1e293b', backgroundColor: 'rgba(2, 6, 23, 0.4)', zIndex: 1000, position: 'relative', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
//         <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
//           <Map size={20} color="#3b82f6" />
//           <h3 style={{ margin: 0, color: '#e4e4e7', fontSize: '1.1rem', fontWeight: '600' }}>Live Map Overview</h3>
//         </div>
//         <button 
//           onClick={() => navigate('/live-map')}
//           style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid #1e293b', padding: '0.4rem 0.75rem', borderRadius: '6px', color: '#a1a1aa', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', transition: 'all 0.2s' }}
//           onMouseOver={e => e.currentTarget.style.color = '#f4f4f5'}
//           onMouseOut={e => e.currentTarget.style.color = '#a1a1aa'}
//         >
//           <Maximize2 size={14} /> Expand
//         </button>
//       </div>
      
//       {/* Map Container */}
//       <div style={{ flex: 1, position: 'relative', backgroundColor: '#020617' }}>
//         <MapContainer 
//           center={centerPos} 
//           zoom={13} 
//           zoomControl={false}
//           scrollWheelZoom={false}
//           style={{ height: '100%', width: '100%', zIndex: 1 }}
//         >
//           <TileLayer
//             attribution='&copy; OpenStreetMap contributors'
//             url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//           />
//           <Marker position={[37.7849, -122.4094]} icon={redMini}>
//             <Popup>Critical Source detected</Popup>
//           </Marker>
//           <Marker position={[37.7649, -122.4294]} icon={orangeMini} />
//           <Marker position={[37.7749, -122.4394]} icon={orangeMini} />
//         </MapContainer>

//         {/* Overlay Vignette to blend edges */}
//         <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', boxShadow: 'inset 0 0 50px 20px rgba(2, 6, 23, 0.7)', zIndex: 10 }}></div>
//       </div>
//     </div>
//   );
// }


import { Maximize2, Map, Flame } from "lucide-react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getFireInsights } from "../../services/fireApi";

// ================= Backend API =================
const API_URL = "https://thermoscope-qaq0.onrender.com/fires";

// ================= Fire Icons ==================
const createFireIcon = (emoji, color, intensity = "Moderate", windDegree = 0) => {
  const intensityColors = {
    "Low":      "#22C55E",
    "Moderate": "#EAB308",
    "High":     "#F97316",
    "Extreme":  "#DC2626",
  };
  const intColor = intensityColors[intensity] || color;
  const spreadDegree = (windDegree + 180) % 360;

  return L.divIcon({
    className: "custom-fire-marker",
    html: `
      <div style="position:relative; width:34px; height:34px;">
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
          width:34px;
          height:34px;
          border-radius:50%;
          background:${color};
          display:flex;
          align-items:center;
          justify-content:center;
          font-size:18px;
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
            animation: firePulse 2s infinite;
          "></span>
        </div>
      </div>

      <style>
        @keyframes firePulse{
          0%{transform:scale(.8);opacity:.8;}
          70%{transform:scale(1.6);opacity:0;}
          100%{transform:scale(1.6);opacity:0;}
        }
      </style>
    `,
    iconSize: [34, 49],
    iconAnchor: [17, 34],
    popupAnchor: [0, -34],
  });
};

const FIRE_TYPE_CONFIG = {
  "Industrial Fire": { emoji: "🏭", color: "#EF4444" },
  "Commercial Fire": { emoji: "🏢", color: "#2563EB" },
  "Forest Fire": { emoji: "🌲", color: "#16A34A" },
  "Agricultural Fire": { emoji: "🌾", color: "#EAB308" },
  "Residential Fire": { emoji: "🏠", color: "#EC4899" },
};

const DEFAULT_ICON = createFireIcon("🔥", "#F97316", "Moderate", 0);

// Intensity badge colors
const intensityColors = {
  Low: "#22C55E",
  Moderate: "#EAB308",
  High: "#F97316",
  Extreme: "#DC2626",
};

export default function MapMockup() {
  const navigate = useNavigate();

  const [fires, setFires] = useState([]);
  const [loading, setLoading] = useState(true);

  const indiaCenter = [22.9734, 78.6569];

  useEffect(() => {
    loadFireData();
  }, []);

  const loadFireData = async () => {
    try {
      const response = await fetch(API_URL);

      if (!response.ok) throw new Error("Unable to fetch fire data.");

      const data = await response.json();

      setFires(data.fires || []);
    } catch (err) {
      console.error("Fire API Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="thermal-card"
      style={{
        height: "460px",
        padding: 0,
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        borderRadius: "18px",
      }}
    >
      {/* ================= Header ================= */}

      <div
        style={{
          padding: "18px",
          borderBottom: "1px solid #1e293b",
          background: "rgba(2,6,23,.6)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          zIndex: 1000,
        }}
      >
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <Map color="#3B82F6" size={20} />
          <div>
            <h3
              style={{
                margin: 0,
                color: "#F8FAFC",
                fontWeight: 600,
                fontSize: "1.05rem",
              }}
            >
              Live Fire Classification Map
            </h3>

            <span
              style={{
                color: "#94A3B8",
                fontSize: ".8rem",
              }}
            >
              Geoapify + Groq Classified Hotspots
            </span>
          </div>
        </div>

        <button
          onClick={() => navigate("/live-map")}
          style={{
            background: "rgba(255,255,255,.05)",
            border: "1px solid #334155",
            padding: "8px 12px",
            borderRadius: 8,
            color: "#CBD5E1",
            display: "flex",
            gap: 8,
            cursor: "pointer",
          }}
        >
          <Maximize2 size={15} />
          Expand
        </button>
      </div>

      {/* ================= Map ================= */}

      <div style={{ flex: 1, position: "relative" }}>
        <MapContainer
          center={indiaCenter}
          zoom={4}
          zoomControl={false}
          scrollWheelZoom={true}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution="© OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Dynamic Fire Markers */}

          {fires.map((fire, index) => {
            const config = FIRE_TYPE_CONFIG[fire.fire_type];
            const icon = config ? createFireIcon(config.emoji, config.color, fire.intensity, fire.wind_degree || 0) : DEFAULT_ICON;
            
            return (
            <Marker
              key={index}
              position={[fire.latitude, fire.longitude]}
              icon={icon}
            >
              <Popup minWidth={260}>
                <div style={{ fontFamily: "Inter,sans-serif" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      marginBottom: 10,
                    }}
                  >
                    <Flame color="#DC2626" size={18} />

                    <h3
                      style={{
                        margin: 0,
                        color: "#111827",
                        fontSize: "1rem",
                      }}
                    >
                      {fire.fire_type}
                    </h3>
                  </div>

                  <p style={{ margin: "4px 0", color: "#475569" }}>
                    📍 <strong>{fire.city}</strong>, {fire.country}
                  </p>

                  <div
                    style={{
                      display: "inline-block",
                      marginTop: 6,
                      marginBottom: 10,
                      marginRight: 8,
                      padding: "5px 10px",
                      borderRadius: 999,
                      background:
                        (intensityColors[fire.intensity] || "#64748B") + "22",
                      color: intensityColors[fire.intensity] || "#475569",
                      fontWeight: 700,
                      fontSize: ".8rem",
                    }}
                  >
                    🔥 {fire.intensity}
                  </div>

                  <div style={{
                    display: 'inline-block', marginTop: 6, marginBottom: 10,
                    padding: '5px 10px', borderRadius: 999,
                    background: '#EF444422',
                    color: '#EF4444',
                    fontWeight: 700, fontSize: '.8rem',
                  }}>
                    ⚠️ Risk: {getFireInsights(fire).risk}
                  </div>

                  <div
                    style={{
                      fontSize: ".75rem",
                      color: "#64748B",
                      marginBottom: 10,
                    }}
                  >
                    Latitude : {Number(fire.latitude).toFixed(4)}
                    <br />
                    Longitude : {Number(fire.longitude).toFixed(4)}
                  </div>

                  <div
                    style={{
                      background: "#F8FAFC",
                      borderRadius: 8,
                      padding: 10,
                    }}
                  >
                    <div
                      style={{
                        fontSize: ".78rem",
                        fontWeight: 700,
                        color: "#2563EB",
                        marginBottom: 5,
                      }}
                    >
                      AI Reasoning & Insights
                    </div>

                    <p
                      style={{
                        margin: 0,
                        color: "#334155",
                        fontSize: ".75rem",
                        lineHeight: 1.5,
                      }}
                    >
                      <strong>Prediction:</strong> {getFireInsights(fire).prediction}
                    </p>
                    <p
                      style={{
                        margin: "4px 0 0 0",
                        color: "#334155",
                        fontSize: ".75rem",
                        lineHeight: 1.5,
                      }}
                    >
                      <strong>Cause:</strong> {getFireInsights(fire).causes}
                    </p>
                  </div>
                </div>
              </Popup>
            </Marker>
            );
          })}
        </MapContainer>

        {/* Loading */}

        {loading && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "rgba(2,6,23,.85)",
              color: "#E2E8F0",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              zIndex: 999,
            }}
          >
            Loading Fire Hotspots...
          </div>
        )}

        {/* Legend */}

        <div
          style={{
            position: "absolute",
            bottom: 15,
            left: 15,
            background: "rgba(15,23,42,.9)",
            backdropFilter: "blur(8px)",
            padding: "12px 14px",
            borderRadius: 12,
            color: "#F8FAFC",
            zIndex: 999,
            border: "1px solid #334155",
            minWidth: 170,
          }}
        >
          <div
            style={{
              fontWeight: 600,
              marginBottom: 10,
            }}
          >
            Fire Types
          </div>

          <Legend emoji="🏭" color="#EF4444" label="Industrial Fire" />
          <Legend emoji="🏢" color="#2563EB" label="Commercial Fire" />
          <Legend emoji="🌲" color="#16A34A" label="Forest Fire" />
          <Legend emoji="🌾" color="#EAB308" label="Agricultural Fire" />
          <Legend emoji="🏠" color="#EC4899" label="Residential Fire" />
        </div>
      </div>
    </div>
  );
}

// ================= Legend =================

function Legend({ emoji, color, label }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        marginBottom: 6,
      }}
    >
      <div
        style={{
          width: 18,
          height: 18,
          borderRadius: "50%",
          background: color,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 10,
        }}
      >
        {emoji}
      </div>

      <span style={{ fontSize: ".78rem" }}>{label}</span>
    </div>
  );
}
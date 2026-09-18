import { useEffect, useState } from 'react';
import { AlertTriangle, Info, ShieldAlert, Target, Activity, MapPin } from 'lucide-react';
import { fetchFireLocations, getFireInsights } from '../../services/fireApi';

export default function LiveFeed() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadFires() {
      try {
        const fires = await fetchFireLocations();
        
        // Generate live feed alerts from the fire data
        const newAlerts = fires.map((fire, index) => {
          const insights = getFireInsights(fire);
          
          let icon = Info;
          let color = '#3b82f6';
          let type = 'info';
          
          if (insights.risk === 'Critical') {
            icon = ShieldAlert;
            color = '#ef4444';
            type = 'critical';
          } else if (insights.risk === 'Elevated') {
            icon = AlertTriangle;
            color = '#f97316';
            type = 'warning';
          }
          
          return {
            id: fire.id || index,
            type,
            fire_type: fire.fire_type,
            area: `${fire.city || 'Unknown City'}, ${fire.country || 'Unknown Country'}`,
            landuse: fire.landuse || 'Unknown',
            prediction: insights.prediction,
            damage: insights.damage,
            risk: insights.risk,
            intensity: fire.intensity,
            icon,
            color,
            time: fire.acq_time ? `Recorded at ${fire.acq_time}` : 'Recent',
          };
        });
        
        // Sort by risk (Critical first)
        newAlerts.sort((a, b) => {
          const riskWeight = { 'Critical': 3, 'Elevated': 2, 'Low': 1 };
          return (riskWeight[b.risk] || 0) - (riskWeight[a.risk] || 0);
        });

        setAlerts(newAlerts);
      } catch (err) {
        console.error("Failed to fetch fires for live feed", err);
      } finally {
        setLoading(false);
      }
    }
    
    loadFires();
    
    // Refresh every 60 seconds
    const interval = setInterval(loadFires, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="thermal-card" style={{ padding: 0, height: '450px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '1.5rem', borderBottom: '1px solid #1e293b', backgroundColor: 'rgba(2, 6, 23, 0.4)' }}>
        <h3 style={{ margin: 0, color: '#e4e4e7', fontSize: '1.2rem', fontWeight: '500' }}>Live Intelligence Feed</h3>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#71717a' }}>Loading feed...</div>
        ) : alerts.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#71717a' }}>No active intelligence alerts.</div>
        ) : (
          alerts.map(alert => {
            const Icon = alert.icon;
            return (
              <div key={alert.id} style={{ display: 'flex', gap: '1rem', padding: '1.25rem', borderBottom: '1px solid #1e293b', alignItems: 'flex-start' }}>
                <div style={{ backgroundColor: `${alert.color}15`, padding: '0.75rem', borderRadius: '12px', color: alert.color, border: `1px solid ${alert.color}40` }}>
                  <Icon size={22} />
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h4 style={{ margin: 0, color: alert.color, fontSize: '1rem', fontWeight: '600' }}>
                      {alert.risk} Risk • {alert.fire_type}
                    </h4>
                    <span style={{ color: '#71717a', fontSize: '0.75rem', fontWeight: '500' }}>{alert.time}</span>
                  </div>
                  
                  {/* Area Field */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#e4e4e7', fontSize: '0.9rem', backgroundColor: 'rgba(255,255,255,0.05)', padding: '0.4rem 0.6rem', borderRadius: '6px', width: 'fit-content' }}>
                    <MapPin size={14} color="#94a3b8" />
                    <strong>Area:</strong> {alert.area} <span style={{ color: '#71717a', fontSize: '0.8rem' }}>({alert.landuse})</span>
                  </div>
                  
                  {/* Insights Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.4rem', marginTop: '0.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                      <Activity size={14} color="#3b82f6" style={{ marginTop: '0.2rem', flexShrink: 0 }} />
                      <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.85rem', lineHeight: '1.4' }}>
                        <span style={{ color: '#93c5fd', fontWeight: '600' }}>Prediction:</span> {alert.prediction}
                      </p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                      <ShieldAlert size={14} color="#ef4444" style={{ marginTop: '0.2rem', flexShrink: 0 }} />
                      <p style={{ margin: 0, color: '#cbd5e1', fontSize: '0.85rem', lineHeight: '1.4' }}>
                        <span style={{ color: '#fca5a5', fontWeight: '600' }}>Damage:</span> {alert.damage}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  );
}

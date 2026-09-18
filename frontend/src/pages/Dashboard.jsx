import { useState, useEffect } from 'react';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import KPICard from '../components/dashboard/KPICard';
import MapMockup from '../components/map/MapMockup';
import LiveFeed from '../components/dashboard/LiveFeed';
import HeatTrendChart from '../components/analytics/HeatTrendChart';
import AnomalyDistributionChart from '../components/analytics/AnomalyDistributionChart';
import SourceTypeChart from '../components/analytics/SourceTypeChart';
import { Flame, AlertCircle, Crosshair, Map, Satellite, BrainCircuit } from 'lucide-react';
import { fetchDashboardStats } from '../services/fireApi';

export default function Dashboard() {
  const [stats, setStats] = useState({
    kpis: {
      active_fires: "-",
      critical_alerts: "-",
      persistent_sources: "-",
      monitored_area: "-",
      satellites: "-",
      ai_confidence: "-"
    },
    charts: {
      heatTrend: [],
      regionData: [],
      sourceData: []
    }
  });

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchDashboardStats();
        setStats(data);
      } catch (err) {
        console.error("Failed to load dashboard stats", err);
      }
    };
    loadStats();
    // Refresh stats every 5 minutes if FIRMS_API_KEY is used, but for dataset fallback once is enough.
    const interval = setInterval(loadStats, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div style={{ maxWidth: '1400px', width: '100%', margin: '0 auto', paddingBottom: '2rem' }}>
      <DashboardHeader />
      
      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <KPICard title="Active Fires" value={stats.kpis.active_fires} trend="Live" icon={Flame} color="#3b82f6" />
        <KPICard title="Critical Alerts" value={stats.kpis.critical_alerts} trend="FRP>50" icon={AlertCircle} color="#f97316" />
        <KPICard title="Persistent Sources" value={stats.kpis.persistent_sources} trend="Est." icon={Crosshair} color="#0ea5e9" />
        <KPICard title="Monitored Area" value={stats.kpis.monitored_area} trend="sq km" icon={Map} color="#10b981" />
        <KPICard title="Satellites Online" value={stats.kpis.satellites} icon={Satellite} color="#3b82f6" />
        <KPICard title="AI Confidence" value={stats.kpis.ai_confidence} trend="Avg" icon={BrainCircuit} color="#8b5cf6" />
      </div>

      {/* Main Grid: Map & Feed */}
      <div className="dashboard-main-grid">
        <MapMockup />
        <LiveFeed />
      </div>

      {/* Analytics Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <HeatTrendChart data={stats.charts.heatTrend} />
        <AnomalyDistributionChart data={stats.charts.regionData} />
        <SourceTypeChart data={stats.charts.sourceData} />
      </div>
    </div>
  );
}

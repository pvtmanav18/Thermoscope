// ==========================================
// services/fireApi.js
// API Service — Agni Chakshu Frontend
// Connects to the FastAPI backend for
// classified fire data.
// ==========================================

const API_BASE = "https://thermoscope-qaq0.onrender.com";

/**
 * Fetch classified fire locations from the backend.
 * Returns an array of fire objects with: id, latitude, longitude,
 * country, city, fire_type, intensity, reasoning, confidence, etc.
 */
export async function fetchFireLocations() {
  const response = await fetch(`${API_BASE}/fires`);

  if (!response.ok) {
    throw new Error("Unable to fetch fire locations from backend.");
  }

  const data = await response.json();

  return data.fires || [];
}

/**
 * Fetch raw unclassified fire locations from the dataset.
 */
export async function fetchRawFireLocations() {
  const response = await fetch(`${API_BASE}/raw-fires`);

  if (!response.ok) {
    throw new Error("Unable to fetch raw fire locations from backend.");
  }

  const data = await response.json();

  return data.fires || [];
}

/**
 * Fetch classified fires as GeoJSON FeatureCollection.
 * For direct use in mapping libraries.
 */
export async function fetchFiresGeoJSON() {
  const response = await fetch(`${API_BASE}/api/classified-fires`);

  if (!response.ok) {
    throw new Error("Unable to fetch GeoJSON from backend.");
  }

  return await response.json();
}

/**
 * Fetch fire statistics (type distribution, intensity, country).
 */
export async function fetchFireStats() {
  const response = await fetch(`${API_BASE}/api/stats`);

  if (!response.ok) {
    throw new Error("Unable to fetch fire statistics.");
  }

  return await response.json();
}

/**
 * Fetch real-time dashboard KPIs and charts data from backend.
 */
export async function fetchDashboardStats() {
  const response = await fetch(`${API_BASE}/dashboard-stats`);

  if (!response.ok) {
    throw new Error("Unable to fetch dashboard statistics.");
  }

  return await response.json();
}

/**
 * Health check — test backend connectivity.
 * Returns true if backend is reachable.
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Helper to generate fire insights (Risk, Damage, Causes, Prediction).
 */
export const getFireInsights = (fire) => {
  let risk = "Low";
  if (fire.intensity === "Extreme" || fire.intensity === "High") risk = "Critical";
  else if (fire.intensity === "Moderate") risk = "Elevated";

  let damage = "Minimal";
  if (fire.fire_type === "Forest Fire" && risk === "Critical") damage = "Severe ecological damage, habitat loss";
  else if (fire.fire_type === "Industrial Fire") damage = "High infrastructure damage, chemical hazard";
  else if (fire.fire_type === "Residential Fire") damage = "High property loss, civilian risk";
  else if (fire.fire_type === "Commercial Fire") damage = "Property and economic loss";
  else damage = "Crop damage, soil degradation";

  let causes = "Unknown";
  if (fire.fire_type === "Forest Fire") causes = "Lightning, dry vegetation, human negligence";
  else if (fire.fire_type === "Agricultural Fire") causes = "Stubble burning, land clearing";
  else if (fire.fire_type === "Industrial Fire") causes = "Equipment failure, chemical reaction";
  else if (fire.fire_type === "Residential Fire") causes = "Electrical fault, cooking accident";
  else if (fire.fire_type === "Commercial Fire") causes = "Electrical fault, arson";

  let prediction = fire.rule_prediction || (fire.wind_speed > 15 ? "Expected to spread rapidly in wind direction." : "Expected to spread slowly.");

  return { risk, damage, causes, prediction };
};

/**
 * Local classification algorithm based on raw dataset features.
 */
export const classifyFireLocal = (fire) => {
  let fire_type = "Unknown";
  let intensity = "Low";
  let reasoning = "Classified based on raw FRP and environmental data.";

  // Determine intensity based on FRP (Fire Radiative Power)
  if (fire.frp > 100) intensity = "Extreme";
  else if (fire.frp > 50) intensity = "High";
  else if (fire.frp > 20) intensity = "Moderate";

  // Determine Fire Type based on properties like brightness and FRP
  if (fire.bright_ti4 > 330 && fire.frp > 80) fire_type = "Industrial Fire";
  else if (fire.bright_ti4 > 310 && fire.frp > 40) fire_type = "Forest Fire";
  else if (fire.frp > 15) fire_type = "Agricultural Fire";
  else fire_type = "Residential Fire";
  
  // Attach default placeholders for missing properties
  return {
    ...fire,
    fire_type,
    intensity,
    reasoning,
    city: fire.city || "Unknown",
    country: fire.country || "Unknown",
    rule_prediction: fire.wind_speed > 15 ? "High wind warning, rapid spread likely." : "Stable conditions.",
  };
};
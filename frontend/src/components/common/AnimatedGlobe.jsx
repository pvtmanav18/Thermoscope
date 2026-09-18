import React, { useMemo } from 'react';
import './AnimatedGlobe.css';

export default function AnimatedGlobe() {
  // Generate 23 random satellites
  const satellites = useMemo(() => {
    const colors = ['#3b82f6', '#f97316', '#10b981', '#fbbf24', '#a855f7', '#ec4899', '#06b6d4', '#eab308', '#f43f5e', '#8b5cf6'];
    const sats = [];
    for (let i = 0; i < 23; i++) {
      sats.push({
        id: i,
        orbitSize: Math.floor(Math.random() * 800) + 1200, // 1200px to 2000px
        duration: Math.floor(Math.random() * 40) + 15, // 15s to 55s
        tiltX: Math.floor(Math.random() * 120) + 20, // 20deg to 140deg
        tiltY: Math.floor(Math.random() * 120) - 60, // -60deg to 60deg
        size: Math.floor(Math.random() * 10) + 4, // 4px to 13px
        color: colors[Math.floor(Math.random() * colors.length)],
        direction: Math.random() > 0.5 ? 'normal' : 'reverse',
      });
    }
    return sats;
  }, []);

  return (
    <div className="globe-container">
      {/* Background space/stars */}
      <div className="space-background"></div>
      
      {/* The zooming container to handle the initial drop-in animation */}
      <div className="globe-zoom-wrapper">
        <div className="globe-wrapper">
          {/* The rotating Earth with night map */}
          <div className="earth"></div>
          
          {/* Atmospheric Edge & Sun Flare */}
          <div className="atmosphere"></div>
          <div className="sun-flare"></div>
          
          {/* Dynamic Satellites */}
          {satellites.map((sat) => (
            <div 
              key={sat.id}
              className="satellite-orbit-container"
              style={{
                width: sat.orbitSize,
                height: sat.orbitSize,
                transform: `rotateX(${sat.tiltX}deg) rotateY(${sat.tiltY}deg)`,
              }}
            >
              <div 
                className="satellite-spinner"
                style={{
                  animationDuration: `${sat.duration}s`,
                  animationDirection: sat.direction,
                }}
              >
                <div 
                  className="satellite-dot"
                  style={{
                    width: sat.size,
                    height: sat.size,
                    backgroundColor: sat.color,
                    boxShadow: `0 0 ${sat.size * 1.5}px ${sat.color}`,
                    left: 0,
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import './AnimatedStats.css';

const AnimatedStats = ({ textsFound, confidence, dataSources, isVisible }) => {
  const [animatedTexts, setAnimatedTexts] = useState(0);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);
  const [animatedSources, setAnimatedSources] = useState(0);

  useEffect(() => {
    if (!isVisible) return;

    // Animate numbers with staggered timing
    const animateValue = (start, end, duration, setter) => {
      const startTime = Date.now();
      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.round(start + (end - start) * easeOutQuart);
        setter(current);
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      requestAnimationFrame(animate);
    };

    // Staggered animations
    setTimeout(() => animateValue(0, textsFound, 1000, setAnimatedTexts), 200);
    setTimeout(() => animateValue(0, confidence, 1500, setAnimatedConfidence), 500);
    setTimeout(() => animateValue(0, dataSources, 800, setAnimatedSources), 800);
  }, [isVisible, textsFound, confidence, dataSources]);

  const getConfidenceColor = (conf) => {
    if (conf >= 80) return 'var(--accent-green)';
    if (conf >= 60) return 'var(--accent-yellow)';
    return 'var(--accent-orange)';
  };

  const getConfidenceIcon = (conf) => {
    if (conf >= 80) return '🎯';
    if (conf >= 60) return '✅';
    return '⚠️';
  };

  return (
    <div className={`animated-stats ${isVisible ? 'visible' : ''}`}>
      <div className="stats-container">
        
        {/* Texts Found */}
        <div className="stat-card texts-stat">
          <div className="stat-icon">
            <div className="icon-wrapper">
              📝
              <div className="icon-pulse"></div>
            </div>
          </div>
          <div className="stat-content">
            <div className="stat-number">
              <span className="number">{animatedTexts}</span>
              <div className="number-trail"></div>
            </div>
            <div className="stat-label">Texts Detected</div>
            <div className="stat-bar">
              <div 
                className="stat-fill texts-fill"
                style={{ width: isVisible ? `${Math.min(textsFound * 20, 100)}%` : '0%' }}
              ></div>
            </div>
          </div>
        </div>

        {/* Confidence */}
        <div className="stat-card confidence-stat">
          <div className="stat-icon">
            <div className="icon-wrapper">
              {getConfidenceIcon(confidence)}
              <div className="confidence-ring">
                <svg viewBox="0 0 36 36" className="circular-chart">
                  <path className="circle-bg"
                    d="M18 2.0845
                      a 15.9155 15.9155 0 0 1 0 31.831
                      a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path className="circle"
                    strokeDasharray={`${isVisible ? animatedConfidence : 0}, 100`}
                    d="M18 2.0845
                      a 15.9155 15.9155 0 0 1 0 31.831
                      a 15.9155 15.9155 0 0 1 0 -31.831"
                    style={{ stroke: getConfidenceColor(confidence) }}
                  />
                </svg>
              </div>
            </div>
          </div>
          <div className="stat-content">
            <div className="stat-number">
              <span className="number" style={{ color: getConfidenceColor(confidence) }}>
                {animatedConfidence}%
              </span>
              <div className="confidence-sparkle">✨</div>
            </div>
            <div className="stat-label">AI Confidence</div>
            <div className="confidence-level">
              {confidence >= 80 ? 'High Accuracy' : 
               confidence >= 60 ? 'Good Match' : 'Analyzing...'}
            </div>
          </div>
        </div>

        {/* Data Sources */}
        <div className="stat-card sources-stat">
          <div className="stat-icon">
            <div className="icon-wrapper">
              🗃️
              <div className="sources-dots">
                <div className="dot dot1"></div>
                <div className="dot dot2"></div>
                <div className="dot dot3"></div>
              </div>
            </div>
          </div>
          <div className="stat-content">
            <div className="stat-number">
              <span className="number">{animatedSources}</span>
              <div className="sources-network">
                <div className="network-line line1"></div>
                <div className="network-line line2"></div>
                <div className="network-line line3"></div>
              </div>
            </div>
            <div className="stat-label">Data Sources</div>
            <div className="sources-list">
              <span className="source-badge ai">🤖 AI</span>
              <span className="source-badge ocr">📖 OCR</span>
              <span className="source-badge db">🗄️ DB</span>
            </div>
          </div>
        </div>

      </div>

      {/* Floating Success Particles */}
      <div className="success-particles">
        <div className="particle particle-1">⭐</div>
        <div className="particle particle-2">✨</div>
        <div className="particle particle-3">🎯</div>
        <div className="particle particle-4">💫</div>
        <div className="particle particle-5">⚡</div>
      </div>
    </div>
  );
};

export default AnimatedStats;
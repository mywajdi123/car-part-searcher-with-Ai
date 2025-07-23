import React, { useState, useEffect } from 'react';
import './InteractivePartCard.css';

const InteractivePartCard = ({ partData, onPartClick, isVisible }) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!isVisible) return;

    const steps = [
      () => setCurrentStep(1), // Show part type
      () => setCurrentStep(2), // Show category  
      () => setCurrentStep(3), // Show condition
      () => setCurrentStep(4), // Show confidence
      () => setIsRevealed(true) // Full reveal
    ];

    steps.forEach((step, index) => {
      setTimeout(step, (index + 1) * 400);
    });
  }, [isVisible]);

  if (!partData?.ai_analysis) return null;

  const {
    part_identification,
    physical_specs,
    confidence_scores,
    part_type,
    category,
    condition,
    confidence
  } = partData.ai_analysis;

  const displayPartType = part_identification?.part_type || part_type || 'Unknown Part';
  const displayCategory = part_identification?.category || category || 'Unknown';
  const displayCondition = physical_specs?.condition || condition || 'Unknown';
  const displayConfidence = Math.round((confidence_scores?.overall || confidence || 0) * 100);

  const getCategoryIcon = (cat) => {
    const icons = {
      'Engine': '🔧',
      'Electrical': '⚡',
      'Brakes': '🛑',
      'Suspension': '🏗️',
      'Transmission': '⚙️',
      'Cooling': '❄️',
      'Fuel': '⛽',
      'Exhaust': '💨',
      'Body': '🚗',
      'Interior': '🪑'
    };
    return icons[cat] || '🔩';
  };

  const getConditionColor = (cond) => {
    const colors = {
      'New': 'var(--accent-green)',
      'Used': 'var(--accent-blue)',
      'Refurbished': 'var(--accent-purple)',
      'Worn': 'var(--accent-orange)',
      'Unknown': 'var(--text-muted)'
    };
    return colors[cond] || 'var(--text-muted)';
  };

  const getConfidenceLevel = (conf) => {
    if (conf >= 90) return { level: 'Excellent', color: 'var(--accent-green)', icon: '🎯' };
    if (conf >= 75) return { level: 'Very Good', color: 'var(--accent-blue)', icon: '✅' };
    if (conf >= 60) return { level: 'Good', color: 'var(--accent-yellow)', icon: '👍' };
    if (conf >= 40) return { level: 'Fair', color: 'var(--accent-orange)', icon: '⚠️' };
    return { level: 'Low', color: 'var(--accent-red)', icon: '❓' };
  };

  const confidenceInfo = getConfidenceLevel(displayConfidence);

  return (
    <div className={`interactive-part-card ${isVisible ? 'visible' : ''} ${isRevealed ? 'revealed' : ''}`}>
      
      {/* Card Header with Animated Title */}
      <div className="card-header">
        <div className="header-content">
          <div className="title-section">
            <div className="scan-line"></div>
            <h2 className="part-title">
              <span className="title-icon">🔍</span>
              <span className="title-text">Part Identified</span>
            </h2>
            <div className="subtitle">AI Analysis Complete</div>
          </div>
          <div className="header-badge">
            <div className="badge-glow"></div>
            <span>ANALYZED</span>
          </div>
        </div>
      </div>

      {/* Interactive Info Grid */}
      <div className="info-grid">
        
        {/* Part Type */}
        <div className={`info-item part-type-item ${currentStep >= 1 ? 'active' : ''}`}>
          <div className="item-header">
            <div className="item-icon">🔧</div>
            <div className="item-label">Part Type</div>
          </div>
          <div className="item-content">
            <div className="main-value">{displayPartType}</div>
            <div className="typing-indicator">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
          <div className="item-overlay"></div>
        </div>

        {/* Category */}
        <div className={`info-item category-item ${currentStep >= 2 ? 'active' : ''}`}>
          <div className="item-header">
            <div className="item-icon">{getCategoryIcon(displayCategory)}</div>
            <div className="item-label">Category</div>
          </div>
          <div className="item-content">
            <div className="main-value">{displayCategory}</div>
            <div className="category-tag">
              <span className="tag-dot"></span>
              System Component
            </div>
          </div>
          <div className="item-overlay"></div>
        </div>

        {/* Condition */}
        <div className={`info-item condition-item ${currentStep >= 3 ? 'active' : ''}`}>
          <div className="item-header">
            <div className="item-icon">🔍</div>
            <div className="item-label">Condition</div>
          </div>
          <div className="item-content">
            <div 
              className="main-value condition-value"
              style={{ color: getConditionColor(displayCondition) }}
            >
              {displayCondition}
            </div>
            <div className="condition-indicator">
              <div 
                className="condition-bar"
                style={{ backgroundColor: getConditionColor(displayCondition) }}
              ></div>
            </div>
          </div>
          <div className="item-overlay"></div>
        </div>

        {/* Confidence */}
        <div className={`info-item confidence-item ${currentStep >= 4 ? 'active' : ''}`}>
          <div className="item-header">
            <div className="item-icon">{confidenceInfo.icon}</div>
            <div className="item-label">Confidence</div>
          </div>
          <div className="item-content">
            <div className="confidence-display">
              <div 
                className="confidence-percentage"
                style={{ color: confidenceInfo.color }}
              >
                {displayConfidence}%
              </div>
              <div className="confidence-level" style={{ color: confidenceInfo.color }}>
                {confidenceInfo.level}
              </div>
            </div>
            <div className="confidence-meter">
              <div className="meter-track"></div>
              <div 
                className="meter-fill"
                style={{ 
                  width: `${displayConfidence}%`,
                  backgroundColor: confidenceInfo.color 
                }}
              ></div>
              <div className="meter-glow" style={{ background: confidenceInfo.color }}></div>
            </div>
          </div>
          <div className="item-overlay"></div>
        </div>

      </div>

      {/* Function Description */}
      {part_identification?.part_function && (
        <div className={`function-section ${isRevealed ? 'visible' : ''}`}>
          <div className="function-header">
            <div className="function-icon">💡</div>
            <h3>Function</h3>
          </div>
          <div className="function-content">
            <p>{part_identification.part_function}</p>
          </div>
          <div className="function-wave"></div>
        </div>
      )}

      {/* Action Button */}
      <div className={`action-section ${isRevealed ? 'visible' : ''}`}>
        <button 
          className="explore-button"
          onClick={() => onPartClick && onPartClick(partData.part_number)}
        >
          <span className="button-bg"></span>
          <span className="button-content">
            <span className="button-icon">🚀</span>
            <span className="button-text">Explore Compatibility</span>
          </span>
          <div className="button-particles">
            <div className="particle"></div>
            <div className="particle"></div>
            <div className="particle"></div>
          </div>
        </button>
      </div>

      {/* Floating Elements */}
      <div className="floating-elements">
        <div className="float-element element-1">⚡</div>
        <div className="float-element element-2">🔧</div>
        <div className="float-element element-3">✨</div>
        <div className="float-element element-4">🎯</div>
      </div>

      {/* Background Effects */}
      <div className="card-effects">
        <div className="effect-circle circle-1"></div>
        <div className="effect-circle circle-2"></div>
        <div className="effect-circuit">
          <svg viewBox="0 0 200 200" className="circuit-svg">
            <defs>
              <linearGradient id="circuit-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="rgba(102, 126, 234, 0.6)" />
                <stop offset="100%" stopColor="rgba(118, 75, 162, 0.6)" />
              </linearGradient>
            </defs>
            <path 
              d="M20,50 L60,50 L60,90 L140,90 L140,130 L180,130" 
              stroke="url(#circuit-gradient)" 
              strokeWidth="2" 
              fill="none"
              className="circuit-path"
            />
            <circle cx="60" cy="50" r="3" fill="var(--accent-blue)" className="circuit-node" />
            <circle cx="60" cy="90" r="3" fill="var(--accent-purple)" className="circuit-node" />
            <circle cx="140" cy="90" r="3" fill="var(--accent-green)" className="circuit-node" />
          </svg>
        </div>
      </div>

    </div>
  );
};

export default InteractivePartCard;
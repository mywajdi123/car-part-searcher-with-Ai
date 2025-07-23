import React, { useState, useEffect } from 'react';
import CompatibilityView from './CompatibilityView';
import ShoppingResults from './ShoppingResults';
import AnimatedStats from './AnimatedStats';
import InteractivePartCard from './InteractivePartCard';
import './OCRResult.css';

const OCRResult = ({ result, selectedPart, onPartClick, loading }) => {
    const [showStats, setShowStats] = useState(false);
    const [showPartCard, setShowPartCard] = useState(false);
    const [activeTab, setActiveTab] = useState('compatibility');
    const [loadingSteps, setLoadingSteps] = useState(0);

    // Enhanced loading animation
    useEffect(() => {
        if (loading) {
            const stepInterval = setInterval(() => {
                setLoadingSteps(prev => {
                    if (prev >= 3) {
                        clearInterval(stepInterval);
                        return 3;
                    }
                    return prev + 1;
                });
            }, 800);

            return () => clearInterval(stepInterval);
        } else {
            setLoadingSteps(0);
        }
    }, [loading]);

    useEffect(() => {
        if (result && !result.error) {
            // Reset states
            setShowStats(false);
            setShowPartCard(false);
            
            // Trigger animations with delays
            setTimeout(() => setShowStats(true), 500);
            setTimeout(() => setShowPartCard(true), 1200);
        }
    }, [result]);

    // Enhanced tab switching with visual feedback
    const handleTabSwitch = (tabName) => {
        setActiveTab(tabName);
        
        // Add ripple effect
        const button = document.querySelector(`[data-tab="${tabName}"]`);
        if (button) {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = 'scale(1)';
            }, 150);
        }
    };

    // Enhanced part click with visual feedback
    const handlePartClick = (partNumber) => {
        if (onPartClick) {
            // Add click animation
            const partChip = document.querySelector('.highlighted-part');
            if (partChip) {
                partChip.style.transform = 'scale(1.1)';
                partChip.style.boxShadow = '0 0 20px rgba(0, 212, 255, 0.8)';
                setTimeout(() => {
                    partChip.style.transform = 'scale(1)';
                    partChip.style.boxShadow = '';
                }, 300);
            }
            
            onPartClick(partNumber);
        }
    };

    if (loading) {
        return (
            <div className="ocr-result loading">
                <div className="loading-container">
                    <div className="advanced-loader">
                        <div className="loader-ring"></div>
                        <div className="loader-ring"></div>
                        <div className="loader-ring"></div>
                        <div className="loader-core">
                            <div className="scan-beam"></div>
                        </div>
                    </div>
                    <div className="loading-text">
                        <h3>🔍 Analyzing Your Part</h3>
                        <p>Advanced AI is examining the image with computer vision</p>
                        <div className="loading-steps">
                            <div className={`step ${loadingSteps >= 0 ? 'active' : ''}`}>
                                📷 Image Processing
                                {loadingSteps >= 0 && <span className="checkmark">✓</span>}
                            </div>
                            <div className={`step ${loadingSteps >= 1 ? 'active' : ''}`}>
                                🔤 OCR Text Recognition
                                {loadingSteps >= 1 && <span className="checkmark">✓</span>}
                            </div>
                            <div className={`step ${loadingSteps >= 2 ? 'active' : ''}`}>
                                🧠 AI Visual Analysis
                                {loadingSteps >= 2 && <span className="checkmark">✓</span>}
                            </div>
                            <div className={`step ${loadingSteps >= 3 ? 'active' : ''}`}>
                                🗄️ Database Matching
                                {loadingSteps >= 3 && <span className="checkmark">✓</span>}
                            </div>
                        </div>
                    </div>
                </div>
                <div className="loading-particles">
                    {[...Array(8)].map((_, i) => (
                        <div key={i} className="particle" style={{
                            animationDelay: `${i * 0.3}s`,
                            left: `${10 + i * 10}%`,
                            top: `${20 + (i % 3) * 20}%`
                        }}></div>
                    ))}
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="ocr-result empty">
                <div className="empty-state">
                    <div className="empty-animation">
                        <div className="empty-icon">📷</div>
                        <div className="icon-rings">
                            <div className="ring ring-1"></div>
                            <div className="ring ring-2"></div>
                            <div className="ring ring-3"></div>
                        </div>
                    </div>
                    <h3>Ready to Identify Parts</h3>
                    <p>Upload an image to see our advanced AI analysis in action</p>
                    <div className="empty-features">
                        <div className="feature">🎯 99% Accuracy</div>
                        <div className="feature">⚡ Instant Results</div>
                        <div className="feature">🌐 Global Database</div>
                    </div>
                </div>
            </div>
        );
    }

    const hasError = result.error;
    const hasTexts = result.detected_texts && result.detected_texts.length > 0;
    const hasPartNumber = result.part_number;
    const hasAiAnalysis = result.ai_analysis;
    const hasDatabaseResult = result.database_result?.found;

    return (
        <div className="ocr-result enhanced">
            
            {/* Error Display */}
            {hasError && (
                <div className="error-section enhanced-error">
                    <div className="error-animation">
                        <div className="error-icon">⚠️</div>
                        <div className="error-waves">
                            <div className="wave"></div>
                            <div className="wave"></div>
                            <div className="wave"></div>
                        </div>
                    </div>
                    <div className="error-content">
                        <h3>Processing Error</h3>
                        <p>{result.error}</p>
                        <button 
                            onClick={() => window.location.reload()} 
                            className="retry-button enhanced"
                        >
                            <span className="button-bg"></span>
                            <span className="button-text">
                                <span className="icon">🔄</span>
                                Try Again
                            </span>
                        </button>
                    </div>
                </div>
            )}

            {/* Success Flow */}
            {!hasError && (
                <>
                    {/* Animated Stats */}
                    <AnimatedStats
                        textsFound={result.texts_found || 0}
                        confidence={result.overall_confidence ? Math.round(result.overall_confidence * 100) : 0}
                        dataSources={Object.values(result.sources || {}).filter(s => s !== 'not_found').length}
                        isVisible={showStats}
                    />

                    {/* Enhanced Text Detection */}
                    {hasTexts && (
                        <div className="section enhanced-texts">
                            <div className="section-header">
                                <h3>
                                    <span className="header-icon">📖</span>
                                    Detected Text ({result.detected_texts.length})
                                    <span className="scan-indicator"></span>
                                </h3>
                            </div>
                            <div className="texts-showcase">
                                {result.detected_texts.map((text, index) => (
                                    <div 
                                        key={index}
                                        className={`text-chip ${text === result.part_number ? 'highlighted-part' : ''}`}
                                        onClick={() => text === result.part_number && handlePartClick(text)}
                                        style={{ 
                                            animationDelay: `${index * 0.1}s`,
                                            cursor: text === result.part_number ? 'pointer' : 'default'
                                        }}
                                    >
                                        <span className="chip-content">{text}</span>
                                        {text === result.part_number && (
                                            <div className="part-badge">
                                                <span className="badge-text">PART #</span>
                                                <div className="badge-glow"></div>
                                            </div>
                                        )}
                                        <div className="chip-shine"></div>
                                    </div>
                                ))}
                            </div>
                            
                            {!hasPartNumber && (
                                <div className="no-part-alert">
                                    <div className="alert-icon">🔍</div>
                                    <div className="alert-content">
                                        <p>No specific part number pattern detected</p>
                                        <span>AI is analyzing visual characteristics instead</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Interactive Part Card */}
                    {hasAiAnalysis && (
                        <InteractivePartCard
                            partData={result}
                            onPartClick={handlePartClick}
                            isVisible={showPartCard}
                        />
                    )}

                    {/* Enhanced Database Results */}
                    {hasDatabaseResult && (
                        <div className="section enhanced-database">
                            <div className="section-header">
                                <h3>
                                    <span className="header-icon">🗃️</span>
                                    Database Match Found
                                    <div className="success-pulse"></div>
                                </h3>
                            </div>
                            <div className="database-showcase">
                                <div className="db-card">
                                    <div className="db-header">
                                        <div className="db-icon">✅</div>
                                        <div className="db-title">Verified Match</div>
                                        <div className="db-badge">CONFIRMED</div>
                                    </div>
                                    <div className="db-content">
                                        <div className="db-row">
                                            <span className="label">Part Name:</span>
                                            <span className="value">{result.database_result.data.part_name}</span>
                                        </div>
                                        <div className="db-row">
                                            <span className="label">Compatible Vehicles:</span>
                                            <span className="value highlight">
                                                {result.database_result.data.compatibility?.length || 0} found
                                            </span>
                                        </div>
                                        <div className="db-row">
                                            <span className="label">Alternatives:</span>
                                            <span className="value highlight">
                                                {result.database_result.data.interchangeable?.length || 0} options
                                            </span>
                                        </div>
                                    </div>
                                    <div className="db-glow"></div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Enhanced Compatibility and Shopping */}
                    {selectedPart && (
                        <div className="section enhanced-compatibility">
                            <div className="section-header">
                                <h3>
                                    <span className="header-icon">🚗</span>
                                    Vehicle Compatibility & Shopping
                                </h3>
                            </div>
                            
                            {/* Functional Tabbed Interface */}
                            <div className="enhanced-tabs">
                                <div className="tab-nav">
                                    <button 
                                        className={`tab-btn ${activeTab === 'compatibility' ? 'active' : ''}`}
                                        data-tab="compatibility"
                                        onClick={() => handleTabSwitch('compatibility')}
                                    >
                                        <span className="tab-icon">🚗</span>
                                        <span className="tab-text">Compatibility</span>
                                        <div className="tab-indicator"></div>
                                    </button>
                                    <button 
                                        className={`tab-btn ${activeTab === 'shopping' ? 'active' : ''}`}
                                        data-tab="shopping"
                                        onClick={() => handleTabSwitch('shopping')}
                                    >
                                        <span className="tab-icon">🛒</span>
                                        <span className="tab-text">Where to Buy</span>
                                        <div className="tab-indicator"></div>
                                    </button>
                                </div>
                                
                                <div className="tab-content">
                                    {activeTab === 'compatibility' && (
                                        <div className="tab-panel active" id="compatibility">
                                            <CompatibilityView
                                                data={result}
                                                loading={false}
                                                error={null}
                                            />
                                        </div>
                                    )}
                                    {activeTab === 'shopping' && (
                                        <div className="tab-panel active" id="shopping">
                                            <ShoppingResults
                                                partData={result}
                                                loading={false}
                                                error={null}
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Call to Action */}
                    {hasPartNumber && !selectedPart && (
                        <div className="section cta-section">
                            <div className="cta-content">
                                <div className="cta-header">
                                    <h3>Ready to Explore?</h3>
                                    <p>Discover vehicle compatibility and find the best prices</p>
                                </div>
                                <button
                                    onClick={() => handlePartClick(result.part_number)}
                                    className="cta-button mega"
                                >
                                    <div className="button-bg"></div>
                                    <div className="button-content">
                                        <span className="button-icon">🚀</span>
                                        <span className="button-text">
                                            <span className="main-text">View Full Report</span>
                                            <span className="sub-text">Compatibility • Pricing • Shopping</span>
                                        </span>
                                    </div>
                                    <div className="button-particles">
                                        <div className="particle"></div>
                                        <div className="particle"></div>
                                        <div className="particle"></div>
                                        <div className="particle"></div>
                                    </div>
                                </button>
                            </div>
                            <div className="cta-background">
                                <div className="bg-circle circle-1"></div>
                                <div className="bg-circle circle-2"></div>
                            </div>
                        </div>
                    )}
                </>
            )}

        </div>
    );
};

export default OCRResult;
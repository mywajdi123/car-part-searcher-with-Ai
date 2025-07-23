import React, { useState, useEffect } from 'react';
import CompatibilityView from './CompatibilityView';
import ShoppingResults from './ShoppingResults';
import AnimatedStats from './AnimatedStats';
import InteractivePartCard from './InteractivePartCard';
import { refreshTabs } from './TabManager';
import './OCRResult.css';

const OCRResult = ({ result, selectedPart, onPartClick, loading }) => {
    const [compatibilityLoading, setCompatibilityLoading] = useState(false);
    const [compatibilityError, setCompatibilityError] = useState(null);
    const [showStats, setShowStats] = useState(false);
    const [showPartCard, setShowPartCard] = useState(false);

    useEffect(() => {
        if (result && !result.error) {
            // Trigger animations with delays
            setTimeout(() => setShowStats(true), 500);
            setTimeout(() => setShowPartCard(true), 1200);
        }
    }, [result]);

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
                        <p>AI is examining the image with advanced computer vision</p>
                        <div className="loading-steps">
                            <div className="step active">📷 Image Processing</div>
                            <div className="step">🔤 Text Recognition</div>
                            <div className="step">🧠 AI Analysis</div>
                            <div className="step">🗄️ Database Search</div>
                        </div>
                    </div>
                </div>
                <div className="loading-particles">
                    <div className="particle"></div>
                    <div className="particle"></div>
                    <div className="particle"></div>
                    <div className="particle"></div>
                    <div className="particle"></div>
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
            
            {/* Error Display with Enhanced Styling */}
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
                    {/* Animated Stats Section */}
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
                                        onClick={() => text === result.part_number && onPartClick && onPartClick(text)}
                                        style={{ animationDelay: `${index * 0.1}s` }}
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
                            onPartClick={onPartClick}
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
                                    <div className="loading-dots">
                                        <span className="dot"></span>
                                        <span className="dot"></span>
                                        <span className="dot"></span>
                                    </div>
                                </h3>
                            </div>
                            
                            {/* Tabbed Interface */}
                            <div className="enhanced-tabs">
                                <div className="tab-nav">
                                    <button className="tab-btn active" data-tab="compatibility">
                                        <span className="tab-icon">🚗</span>
                                        <span className="tab-text">Compatibility</span>
                                        <div className="tab-indicator"></div>
                                    </button>
                                    <button className="tab-btn" data-tab="shopping">
                                        <span className="tab-icon">🛒</span>
                                        <span className="tab-text">Where to Buy</span>
                                        <div className="tab-indicator"></div>
                                    </button>
                                </div>
                                
                                <div className="tab-content">
                                    <div className="tab-panel active" id="compatibility">
                                        <CompatibilityView
                                            data={result}
                                            loading={compatibilityLoading}
                                            error={compatibilityError}
                                        />
                                    </div>
                                    <div className="tab-panel" id="shopping">
                                        <ShoppingResults
                                            partData={result}
                                            loading={compatibilityLoading}
                                            error={compatibilityError}
                                        />
                                    </div>
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
                                    onClick={() => onPartClick && onPartClick(result.part_number)}
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
                                <div className="bg-circuit">
                                    <svg viewBox="0 0 400 200" className="circuit-pattern">
                                        <defs>
                                            <linearGradient id="circuit-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                                <stop offset="0%" stopColor="rgba(102, 126, 234, 0.3)" />
                                                <stop offset="50%" stopColor="rgba(139, 92, 246, 0.5)" />
                                                <stop offset="100%" stopColor="rgba(102, 126, 234, 0.3)" />
                                            </linearGradient>
                                        </defs>
                                        <path d="M0,100 Q100,50 200,100 T400,100" stroke="url(#circuit-grad)" strokeWidth="2" fill="none" className="circuit-line" />
                                        <circle cx="100" cy="75" r="3" fill="var(--accent-blue)" className="circuit-node" />
                                        <circle cx="200" cy="100" r="3" fill="var(--accent-purple)" className="circuit-node" />
                                        <circle cx="300" cy="75" r="3" fill="var(--accent-green)" className="circuit-node" />
                                    </svg>
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}

        </div>
    );
};

export default OCRResult;
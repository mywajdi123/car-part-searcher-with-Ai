import React, { useState, useEffect } from 'react';
import CompatibilityView from './CompatibilityView';
import ShoppingResults from './ShoppingResults';
import './OCRResult.css';

const OCRResult = ({ result, selectedPart, onPartClick, loading }) => {
    const [compatibilityLoading, setCompatibilityLoading] = useState(false);
    const [compatibilityError, setCompatibilityError] = useState(null);

    // Remove this useEffect since we don't need the searchPartInfo function anymore
    // The ShoppingResults component handles shopping data internally

    if (loading) {
        return (
            <div className="ocr-result loading">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <div className="loading-text">
                        <h3>Analyzing Image...</h3>
                        <p>Processing image with AI vision and OCR</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="ocr-result empty">
                <div className="empty-state">
                    <div className="empty-icon">📷</div>
                    <h3>No Image Processed</h3>
                    <p>Upload an image to see OCR and compatibility results</p>
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
        <div className="ocr-result">
            {/* Success Summary */}
            {!hasError && (
                <div className="result-summary">
                    <div className="summary-header">
                        <h2>🔍 Analysis Complete</h2>
                        <div className="summary-stats">
                            <span className="stat">
                                <strong>{result.texts_found || 0}</strong> texts detected
                            </span>
                            <span className="stat">
                                <strong>{result.overall_confidence ? Math.round(result.overall_confidence * 100) : 0}%</strong> confidence
                            </span>
                            <span className="stat">
                                <strong>{Object.values(result.sources || {}).filter(s => s !== 'not_found').length}</strong> data sources
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Error Display */}
            {hasError && (
                <div className="error-section">
                    <div className="error-content">
                        <h3>❌ Processing Error</h3>
                        <p>{result.error}</p>
                        <button onClick={() => window.location.reload()} className="retry-button">
                            Try Again
                        </button>
                    </div>
                </div>
            )}

            {/* OCR Results Section */}
            {hasTexts && (
                <div className="section ocr-texts">
                    <h3>📖 Detected Text ({result.detected_texts.length})</h3>
                    <div className="texts-container">
                        {result.detected_texts.map((text, index) => (
                            <span
                                key={index}
                                className={`text-badge ${text === result.part_number ? 'part-number' : ''}`}
                                onClick={() => text === result.part_number && onPartClick && onPartClick(text)}
                            >
                                {text}
                            </span>
                        ))}
                    </div>
                    {!hasPartNumber && (
                        <div className="no-part-warning">
                            <p>⚠️ No part number pattern detected in the text above</p>
                        </div>
                    )}
                </div>
            )}

            {/* Part Number Section */}
            {hasPartNumber && (
                <div className="section part-number-section">
                    <h3>🔧 Identified Part Number</h3>
                    <div className="part-number-display">
                        <code className="part-number-code">{result.part_number}</code>
                        <button
                            onClick={() => onPartClick && onPartClick(result.part_number)}
                            className="search-part-btn"
                        >
                            Search Part Info
                        </button>
                    </div>
                </div>
            )}

            {/* AI Analysis Quick View */}
            {hasAiAnalysis && (
                <div className="section ai-analysis">
                    <h3>🤖 AI Analysis</h3>
                    <div className="ai-quick-results">
                        <div className="ai-item">
                            <strong>Part Type:</strong>
                            <span>{result.ai_analysis.part_identification?.part_type || result.ai_analysis.part_type || 'Unknown'}</span>
                        </div>
                        <div className="ai-item">
                            <strong>Category:</strong>
                            <span>{result.ai_analysis.part_identification?.category || result.ai_analysis.category || 'Unknown'}</span>
                        </div>
                        <div className="ai-item">
                            <strong>Condition:</strong>
                            <span>{result.ai_analysis.physical_specs?.condition || result.ai_analysis.condition || 'Unknown'}</span>
                        </div>
                        <div className="ai-item">
                            <strong>AI Confidence:</strong>
                            <span className="confidence-score">
                                {Math.round((result.ai_analysis.confidence_scores?.overall || result.ai_analysis.confidence || 0) * 100)}%
                            </span>
                        </div>
                    </div>

                    {result.ai_analysis.part_identification?.part_function && (
                        <div className="part-function">
                            <strong>Function:</strong>
                            <p>{result.ai_analysis.part_identification.part_function}</p>
                        </div>
                    )}
                </div>
            )}

            {/* Database Results */}
            {hasDatabaseResult && (
                <div className="section database-results">
                    <h3>🗃️ Database Match Found</h3>
                    <div className="database-summary">
                        <div className="db-item">
                            <strong>Part Name:</strong>
                            <span>{result.database_result.data.part_name}</span>
                        </div>
                        <div className="db-item">
                            <strong>Compatible Vehicles:</strong>
                            <span>{result.database_result.data.compatibility?.length || 0} found</span>
                        </div>
                        <div className="db-item">
                            <strong>Interchangeable:</strong>
                            <span>{result.database_result.data.interchangeable?.length || 0} alternatives</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Compatibility and Shopping Section - Only show once when part is selected */}
            {selectedPart && (
                <div className="section compatibility-section">
                    <h3>🚗 Compatibility Information</h3>
                    <CompatibilityView
                        data={result}
                        loading={compatibilityLoading}
                        error={compatibilityError}
                    />
                    
                    {/* Shopping Results - integrated into compatibility section */}
                    <div className="shopping-section">
                        <ShoppingResults
                            partData={result}
                            loading={compatibilityLoading}
                            error={compatibilityError}
                        />
                    </div>
                </div>
            )}

            {/* Action Buttons */}
            {hasPartNumber && !selectedPart && (
                <div className="section actions">
                    <button
                        onClick={() => onPartClick && onPartClick(result.part_number)}
                        className="primary-action-btn"
                    >
                        🔍 View Full Compatibility Report
                    </button>
                </div>
            )}
        </div>
    );
};

export default OCRResult;
import React, { useState } from 'react';
import './CompatibilityView.css';

const CompatibilityView = ({ data, loading, error }) => {
    const [activeTab, setActiveTab] = useState('vehicles');
    const [expandedVehicle, setExpandedVehicle] = useState(null);

    if (loading) {
        return (
            <div className="compatibility-loading">
                <div className="loading-spinner"></div>
                <div className="loading-content">
                    <h3>Analyzing Part Compatibility...</h3>
                    <p>Searching multiple databases for vehicle compatibility</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="compatibility-error">
                <div className="error-icon">⚠️</div>
                <h3>Error Loading Compatibility Data</h3>
                <p>{error}</p>
                <button className="retry-btn" onClick={() => window.location.reload()}>
                    Try Again
                </button>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="compatibility-empty">
                <div className="empty-icon">🔍</div>
                <h3>No Compatibility Data Available</h3>
                <p>Upload an image with a visible part number to get compatibility information</p>
            </div>
        );
    }

    const { ai_analysis, database_result, overall_confidence, sources } = data;

    // Get compatibility data from both AI and database
    const aiCompatibility = ai_analysis?.compatibility?.vehicles || [];
    const dbCompatibility = database_result?.data?.compatibility || [];
    const allVehicles = [...aiCompatibility, ...dbCompatibility];

    // Get interchangeable parts
    const aiInterchangeable = ai_analysis?.compatibility?.interchangeable_parts || [];
    const dbInterchangeable = database_result?.data?.interchangeable || [];
    const allInterchangeable = [...aiInterchangeable, ...dbInterchangeable];

    const getConfidenceColor = (confidence) => {
        if (confidence >= 0.9) return '#10b981'; // Green
        if (confidence >= 0.7) return '#f59e0b'; // Yellow
        return '#ef4444'; // Red
    };

    const getConfidenceLabel = (confidence) => {
        if (confidence >= 0.9) return 'High';
        if (confidence >= 0.7) return 'Medium';
        return 'Low';
    };

    return (
        <div className="compatibility-view">
            {/* Header with Part Info */}
            <div className="compatibility-header">
                <div className="part-summary">
                    <div className="part-details">
                        <h2>
                            {database_result?.data?.part_name ||
                                ai_analysis?.part_identification?.part_type ||
                                'Unknown Part'}
                        </h2>
                        <p className="part-number">
                            Part #: <span className="highlight">{data.part_number || 'Not detected'}</span>
                        </p>
                        <div className="part-meta">
                            <span className="category">
                                {database_result?.data?.category || ai_analysis?.part_identification?.category}
                            </span>
                            <span className="confidence-badge" style={{ backgroundColor: getConfidenceColor(overall_confidence) }}>
                                {getConfidenceLabel(overall_confidence)} Confidence ({Math.round(overall_confidence * 100)}%)
                            </span>
                        </div>
                    </div>

                    <div className="data-sources">
                        <h4>Data Sources:</h4>
                        <div className="sources-list">
                            <span className={`source-badge ${sources.ai_vision !== 'rule_based' ? 'active' : ''}`}>
                                🤖 AI Vision
                            </span>
                            <span className={`source-badge ${sources.parts_database !== 'not_found' ? 'active' : ''}`}>
                                🗃️ Parts Database
                            </span>
                            <span className="source-badge active">
                                📖 OCR Text
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="compatibility-tabs">
                <button
                    className={`tab ${activeTab === 'vehicles' ? 'active' : ''}`}
                    onClick={() => setActiveTab('vehicles')}
                >
                    Compatible Vehicles ({allVehicles.length})
                </button>
                <button
                    className={`tab ${activeTab === 'parts' ? 'active' : ''}`}
                    onClick={() => setActiveTab('parts')}
                >
                    Interchangeable Parts ({allInterchangeable.length})
                </button>
                <button
                    className={`tab ${activeTab === 'specs' ? 'active' : ''}`}
                    onClick={() => setActiveTab('specs')}
                >
                    Specifications
                </button>
            </div>

            {/* Tab Content */}
            <div className="tab-content">
                {/* Vehicles Tab */}
                {activeTab === 'vehicles' && (
                    <div className="vehicles-list">
                        {allVehicles.length === 0 ? (
                            <div className="no-data">
                                <p>No vehicle compatibility information found</p>
                            </div>
                        ) : (
                            allVehicles.map((vehicle, index) => (
                                <div
                                    key={index}
                                    className={`vehicle-card ${expandedVehicle === index ? 'expanded' : ''}`}
                                    onClick={() => setExpandedVehicle(expandedVehicle === index ? null : index)}
                                >
                                    <div className="vehicle-header">
                                        <div className="vehicle-info">
                                            <h4>{vehicle.make} {vehicle.model}</h4>
                                            <p className="years">{vehicle.years}</p>
                                        </div>
                                        <div className="vehicle-confidence">
                                            <span
                                                className="confidence-score"
                                                style={{ color: getConfidenceColor(vehicle.confidence || 0.5) }}
                                            >
                                                {Math.round((vehicle.confidence || 0.5) * 100)}%
                                            </span>
                                            <span className="expand-icon">
                                                {expandedVehicle === index ? '▼' : '▶'}
                                            </span>
                                        </div>
                                    </div>

                                    {expandedVehicle === index && (
                                        <div className="vehicle-details">
                                            {vehicle.engines && vehicle.engines.length > 0 && (
                                                <div className="detail-section">
                                                    <strong>Compatible Engines:</strong>
                                                    <ul>
                                                        {vehicle.engines.map((engine, i) => (
                                                            <li key={i}>{engine}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}

                                            {vehicle.trim_levels && vehicle.trim_levels.length > 0 && (
                                                <div className="detail-section">
                                                    <strong>Trim Levels:</strong>
                                                    <p>{vehicle.trim_levels.join(', ')}</p>
                                                </div>
                                            )}

                                            {vehicle.notes && (
                                                <div className="detail-section">
                                                    <strong>Notes:</strong>
                                                    <p className="notes">{vehicle.notes}</p>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                )}

                {/* Interchangeable Parts Tab */}
                {activeTab === 'parts' && (
                    <div className="parts-list">
                        {allInterchangeable.length === 0 ? (
                            <div className="no-data">
                                <p>No interchangeable parts information found</p>
                            </div>
                        ) : (
                            allInterchangeable.map((part, index) => (
                                <div key={index} className="part-card">
                                    <div className="part-header">
                                        <h4>{part.part_number}</h4>
                                        <span className={`part-type ${part.type?.toLowerCase()}`}>
                                            {part.type}
                                        </span>
                                    </div>
                                    <div className="part-details">
                                        <p><strong>Brand:</strong> {part.brand}</p>
                                        {part.price_range && (
                                            <p><strong>Price Range:</strong> {part.price_range}</p>
                                        )}
                                        {part.availability && (
                                            <p><strong>Availability:</strong> {part.availability}</p>
                                        )}
                                        {part.notes && (
                                            <p className="notes">{part.notes}</p>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {/* Specifications Tab */}
                {activeTab === 'specs' && (
                    <div className="specifications">
                        {database_result?.data?.specifications && Object.keys(database_result.data.specifications).length > 0 ? (
                            <div className="specs-grid">
                                {Object.entries(database_result.data.specifications).map(([key, value]) => (
                                    <div key={key} className="spec-item">
                                        <dt>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</dt>
                                        <dd>{value}</dd>
                                    </div>
                                ))}
                            </div>
                        ) : ai_analysis?.physical_specs ? (
                            <div className="specs-grid">
                                {Object.entries(ai_analysis.physical_specs).map(([key, value]) => (
                                    <div key={key} className="spec-item">
                                        <dt>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</dt>
                                        <dd>{Array.isArray(value) ? value.join(', ') : value}</dd>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="no-data">
                                <p>No detailed specifications available</p>
                            </div>
                        )}

                        {/* AI Recommendations */}
                        {ai_analysis?.recommendations && (
                            <div className="recommendations">
                                <h4>🔧 Recommendations</h4>
                                {Object.entries(ai_analysis.recommendations).map(([key, value]) => (
                                    <div key={key} className="recommendation">
                                        <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                                        <p>{value}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default CompatibilityView;
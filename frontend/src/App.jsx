import { useState } from 'react';
import './App.css';
import OCRResult from './components/OCRResult';
import CompatibilityView from './components/CompatibilityView';

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [response, setResponse] = useState(null);
  const [partLinks, setPartLinks] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [selectedPart, setSelectedPart] = useState(null);
  const [compatibilityData, setCompatibilityData] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setResponse(null);
    setPartLinks(null);
    setSelectedPart(null);
    setCompatibilityData(null);

    // Create preview
    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setResponse(null);
    setSelectedPart(null);
    setCompatibilityData(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log("API_URL:", API_URL);
      // Use the new enhanced endpoint
      const endpoint = `${API_URL}/api/predict`;
      console.log("Posting to:", endpoint);
      
      const res = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      
      if (res.ok) {
        setResponse(data);
        setCompatibilityData(data); // Store the enhanced data
        
        // Auto-select part if one was found
        if (data.part_number) {
          setSelectedPart(data.part_number);
        }
      } else {
        setResponse({ error: data.error || 'Upload failed' });
      }
    } catch (err) {
      setResponse({ error: 'Network error: Could not reach server' });
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePartClick = (partNumber) => {
    setSelectedPart(partNumber);
    // Automatically trigger part info lookup when a part is selected
    if (partNumber && !partLinks) {
      handlePartInfo(partNumber);
    }
  };

  const handlePartInfo = async (partNumber = null) => {
    const searchPart = partNumber || response?.part_number;
    if (!searchPart) return;

    setLookupLoading(true);
    try {
      const res = await fetch(`${API_URL}/partinfo/?part_number=${encodeURIComponent(searchPart)}`);
      const data = await res.json();
      setPartLinks(data);
    } catch (err) {
      setPartLinks({ error: 'Lookup failed' });
      console.error("Lookup failed:", err);
    } finally {
      setLookupLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="main-content">
        <div className="header">
          <h1>🔧 Car Parts AI</h1>
          <p>Upload a photo of your car part to identify it and find where to buy it</p>
        </div>

        {/* Upload Section */}
        <div className="upload-section">
          <div className="upload-area">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              id="fileInput"
              style={{ display: 'none' }}
            />
            <label htmlFor="fileInput" className="upload-label">
              <div className="upload-content">
                <div className="upload-icon">📷</div>
                <div className="upload-text">Click to select an image</div>
                <div className="upload-subtext">PNG, JPG, WEBP up to 10MB</div>
              </div>
            </label>
          </div>

          {preview && (
            <div className="preview-container">
              <img src={preview} alt="Preview" className="preview-image" />
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!file || loading}
            className="analyze-button"
          >
            {loading ? '🔍 Analyzing...' : '🚀 Analyze Part'}
          </button>
        </div>

        {/* Enhanced Results Section using OCRResult component */}
        {response && (
          <div className="results-section">
            <OCRResult 
              result={response} 
              selectedPart={selectedPart}
              onPartClick={handlePartClick}
              loading={loading}
            />
          </div>
        )}

        {/* Legacy display for backward compatibility - only show if no enhanced data */}
        {response && !response.ai_analysis && !response.database_result && (
          <div className="legacy-results-section">
            <h2>📋 Analysis Results</h2>
            {response.error ? (
              <div className="error-message">
                ❌ {response.error}
              </div>
            ) : (
              <div className="results-content">
                {/* Basic Info */}
                <div className="info-grid">
                  <div className="info-card">
                    <div className="info-label">File</div>
                    <div className="info-value">{response.filename}</div>
                  </div>
                  <div className="info-card">
                    <div className="info-label">Size</div>
                    <div className="info-value">{response.size_kb} KB</div>
                  </div>
                  <div className="info-card">
                    <div className="info-label">Texts Found</div>
                    <div className="info-value">{response.texts_found}</div>
                  </div>
                </div>

                {/* Car Info */}
                {response.car_info && (
                  <div className="car-info-section">
                    <h3>🚗 Part Identification</h3>
                    <div className="car-info-grid">
                      <div className="car-info-item">
                        <div className="car-info-label">Part Type</div>
                        <div className="car-info-value">{response.car_info.part_type}</div>
                      </div>
                      <div className="car-info-item">
                        <div className="car-info-label">Category</div>
                        <div className="car-info-value">{response.car_info.category}</div>
                      </div>
                      <div className="car-info-item">
                        <div className="car-info-label">Likely Makes</div>
                        <div className="car-info-value">{response.car_info.likely_makes?.join(', ')}</div>
                      </div>
                      <div className="car-info-item">
                        <div className="car-info-label">Year Range</div>
                        <div className="car-info-value">{response.car_info.year_range}</div>
                      </div>
                    </div>
                    <div className="car-info-description">
                      <div className="car-info-label">Description</div>
                      <div className="car-info-value">{response.car_info.description}</div>
                    </div>
                    <div className="confidence-info">
                      Confidence: {Math.round(response.car_info.confidence * 100)}% |
                      {response.car_info.ai_used ? ' AI Enhanced' : ' Rule-based Detection'}
                    </div>
                  </div>
                )}

                {/* Part Number */}
                {response.part_number && (
                  <div className="part-number-section">
                    <div className="part-number-content">
                      <div>
                        <h3>🔢 Part Number Detected</h3>
                        <div className="part-number">{response.part_number}</div>
                      </div>
                      <button
                        onClick={() => handlePartInfo()}
                        disabled={lookupLoading}
                        className="lookup-button"
                      >
                        {lookupLoading ? '🔍 Searching...' : '🛒 Find Online'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Detected Texts */}
                {response.detected_texts && response.detected_texts.length > 0 && (
                  <div className="detected-texts-section">
                    <h3>📝 All Detected Text</h3>
                    <div className="detected-texts-container">
                      {response.detected_texts.map((text, idx) => (
                        <div key={idx} className="detected-text-item">
                          {text}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Standalone Compatibility View - only show if user selected a part but no integrated view */}
        {selectedPart && compatibilityData && !response?.ai_analysis && (
          <div className="compatibility-section">
            <h2>🚗 Compatibility Information</h2>
            <CompatibilityView 
              data={compatibilityData}
              loading={false}
              error={null}
            />
          </div>
        )}

        {/* Shopping Results */}
        {partLinks && (
          <div className="shopping-section">
            <h2>🛒 Where to Buy</h2>
            {partLinks.error ? (
              <div className="error-message">
                ❌ {partLinks.error}
              </div>
            ) : (
              <div className="shopping-content">
                {/* Quick Links */}
                <div className="quick-links">
                  <a href={partLinks.google_url} target="_blank" rel="noopener noreferrer" className="link-button google">
                    🔍 Google Search
                  </a>
                  <a href={partLinks.ebay_url} target="_blank" rel="noopener noreferrer" className="link-button ebay">
                    🏪 eBay Browse
                  </a>
                  <a href={partLinks.amazon_url} target="_blank" rel="noopener noreferrer" className="link-button amazon">
                    📦 Amazon Search
                  </a>
                </div>

                {/* eBay Results */}
                {partLinks.ebay_results && partLinks.ebay_results.length > 0 && (
                  <div className="ebay-results">
                    <h3>🏪 Top eBay Results</h3>
                    <div className="results-grid">
                      {partLinks.ebay_results.map((item, idx) => (
                        <a key={idx} href={item.listing_url} target="_blank" rel="noopener noreferrer" className="result-card">
                          {item.image_url && (
                            <img src={item.image_url} alt={item.title} className="result-image" />
                          )}
                          <div className="result-title">{item.title}</div>
                          <div className="result-price">{item.price}</div>
                          {item.brand && <div className="result-brand">Brand: {item.brand}</div>}
                        </a>
                      ))}
                    </div>
                    <div className="results-count">
                      Found {partLinks.results_count} results
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
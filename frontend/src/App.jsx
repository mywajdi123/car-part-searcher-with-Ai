import { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [response, setResponse] = useState(null);
  const [partLinks, setPartLinks] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lookupLoading, setLookupLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setResponse(null);
    setPartLinks(null);
    
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
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/upload/', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      
      if (res.ok) {
        setResponse(data);
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

  const handlePartInfo = async () => {
    if (!response?.part_number) return;
    
    setLookupLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/partinfo/?part_number=${encodeURIComponent(response.part_number)}`);
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
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 text-blue-400">🔧 Car Parts AI</h1>
          <p className="text-gray-300">Upload a photo of your car part to identify it and find where to buy it</p>
        </div>

        {/* Upload Section */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleFileChange}
                className="hidden"
                id="fileInput"
              />
              <label htmlFor="fileInput" className="cursor-pointer">
                <div className="space-y-2">
                  <div className="text-4xl">📷</div>
                  <div className="text-lg">Click to select an image</div>
                  <div className="text-sm text-gray-400">PNG, JPG, WEBP up to 10MB</div>
                </div>
              </label>
            </div>
            
            {preview && (
              <div className="flex justify-center">
                <img src={preview} alt="Preview" className="max-w-xs max-h-48 rounded-lg border border-gray-600" />
              </div>
            )}
            
            <button 
              onClick={handleSubmit}
              disabled={!file || loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {loading ? '🔍 Analyzing...' : '🚀 Analyze Part'}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {response && (
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold mb-4 text-green-400">📋 Analysis Results</h2>
            
            {response.error ? (
              <div className="bg-red-900 border border-red-500 rounded p-4 text-red-200">
                ❌ {response.error}
              </div>
            ) : (
              <div className="space-y-4">
                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-700 p-3 rounded">
                    <div className="text-sm text-gray-400">File</div>
                    <div className="font-semibold">{response.filename}</div>
                  </div>
                  <div className="bg-gray-700 p-3 rounded">
                    <div className="text-sm text-gray-400">Size</div>
                    <div className="font-semibold">{response.size_kb} KB</div>
                  </div>
                  <div className="bg-gray-700 p-3 rounded">
                    <div className="text-sm text-gray-400">Texts Found</div>
                    <div className="font-semibold">{response.texts_found}</div>
                  </div>
                </div>

                {/* Car Info */}
                {response.car_info && (
                  <div className="bg-blue-900 border border-blue-500 rounded-lg p-4">
                    <h3 className="text-lg font-bold mb-3 text-blue-200">🚗 Part Identification</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-blue-300">Part Type</div>
                        <div className="font-semibold text-white">{response.car_info.part_type}</div>
                      </div>
                      <div>
                        <div className="text-sm text-blue-300">Category</div>
                        <div className="font-semibold text-white">{response.car_info.category}</div>
                      </div>
                      <div>
                        <div className="text-sm text-blue-300">Likely Makes</div>
                        <div className="font-semibold text-white">{response.car_info.likely_makes?.join(', ')}</div>
                      </div>
                      <div>
                        <div className="text-sm text-blue-300">Year Range</div>
                        <div className="font-semibold text-white">{response.car_info.year_range}</div>
                      </div>
                    </div>
                    <div className="mt-3">
                      <div className="text-sm text-blue-300">Description</div>
                      <div className="text-white">{response.car_info.description}</div>
                    </div>
                    <div className="mt-2 text-xs text-blue-400">
                      Confidence: {Math.round(response.car_info.confidence * 100)}% | 
                      {response.car_info.ai_used ? ' AI Enhanced' : ' Rule-based Detection'}
                    </div>
                  </div>
                )}

                {/* Part Number */}
                {response.part_number && (
                  <div className="bg-green-900 border border-green-500 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-green-200">🔢 Part Number Detected</h3>
                        <div className="text-2xl font-mono font-bold text-white">{response.part_number}</div>
                      </div>
                      <button 
                        onClick={handlePartInfo}
                        disabled={lookupLoading}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                      >
                        {lookupLoading ? '🔍 Searching...' : '🛒 Find Online'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Detected Texts */}
                {response.detected_texts && response.detected_texts.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold mb-2 text-yellow-400">📝 All Detected Text</h3>
                    <div className="bg-gray-700 p-3 rounded max-h-32 overflow-y-auto">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {response.detected_texts.map((text, idx) => (
                          <div key={idx} className="text-sm bg-gray-600 px-2 py-1 rounded">
                            {text}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Shopping Results */}
        {partLinks && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-4 text-purple-400">🛒 Where to Buy</h2>
            
            {partLinks.error ? (
              <div className="bg-red-900 border border-red-500 rounded p-4 text-red-200">
                ❌ {partLinks.error}
              </div>
            ) : (
              <div className="space-y-6">
                {/* Quick Links */}
                <div className="flex flex-wrap gap-3">
                  <a href={partLinks.google_url} target="_blank" rel="noopener noreferrer" 
                     className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors">
                    🔍 Google Search
                  </a>
                  <a href={partLinks.ebay_url} target="_blank" rel="noopener noreferrer"
                     className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors">
                    🏪 eBay Browse
                  </a>
                  <a href={partLinks.amazon_url} target="_blank" rel="noopener noreferrer"
                     className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors">
                    📦 Amazon Search
                  </a>
                </div>

                {/* eBay Results */}
                {partLinks.ebay_results && partLinks.ebay_results.length > 0 && (
                  <div>
                    <h3 className="text-lg font-bold mb-3 text-yellow-400">🏪 Top eBay Results</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {partLinks.ebay_results.map((item, idx) => (
                        <a key={idx} href={item.listing_url} target="_blank" rel="noopener noreferrer"
                           className="bg-gray-700 hover:bg-gray-600 rounded-lg p-4 transition-colors block">
                          {item.image_url && (
                            <img src={item.image_url} alt={item.title} 
                                 className="w-full h-32 object-cover rounded mb-3" />
                          )}
                          <div className="font-semibold text-sm mb-2 line-clamp-2">{item.title}</div>
                          <div className="text-green-400 font-bold">{item.price}</div>
                          {item.brand && <div className="text-xs text-gray-400">Brand: {item.brand}</div>}
                        </a>
                      ))}
                    </div>
                    <div className="text-sm text-gray-400 mt-2">
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
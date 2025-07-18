import { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [partLinks, setPartLinks] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResponse(null);
    setPartLinks(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResponse(res.data);
      setPartLinks(null);
    } catch (err) {
      setResponse({ message: 'Upload failed' });
      setPartLinks(null);
      console.error(err);
    }
  };

  const handlePartInfo = async () => {
    if (!response?.part_number) return;
    try {
      const res = await axios.get('http://localhost:8000/partinfo/', {
        params: { part_number: response.part_number }
      });
      setPartLinks(res.data);
      console.log("partLinks:", res.data);   // <-- This should always print, unless never called
    } catch (err) {
      setPartLinks({ error: 'Lookup failed' });
      console.error("Lookup failed:", err);
    }
  };


  return (
    <div style={{ padding: 40 }}>
      <h1>Car Part Image Upload</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {response && (
        <div style={{ marginTop: 20 }}>
          <div><strong>Message:</strong> {response.message}</div>
          {response.filename && <div><strong>Filename:</strong> {response.filename}</div>}
          {response.size_kb && <div><strong>Size (KB):</strong> {response.size_kb}</div>}
          {response.part_number && (
            <div style={{ marginTop: 10 }}>
              <strong>Part Number:</strong> {response.part_number}
              <button style={{ marginLeft: 10 }} onClick={handlePartInfo}>
                Lookup Online
              </button>
            </div>
          )}

          {response.detected_texts && response.detected_texts.length > 0 && (
            <div style={{ marginTop: 10 }}>
              <strong>Detected Texts:</strong>
              <ul>
                {response.detected_texts.map((text, idx) => (
                  <li key={idx}>{text}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      {/* Show eBay detailed results */}
      {partLinks?.ebay_results && partLinks.ebay_results.length > 0 && (
        <div style={{ marginTop: 20 }}>
          <strong>eBay Top Results:</strong>
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {partLinks.ebay_results.map((item, idx) => (
              <div key={idx} style={{ border: "1px solid #333", padding: 10, borderRadius: 8, background: "#222" }}>
                <a href={item.listing_url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none", color: "#66f" }}>
                  <img src={item.image_url} alt={item.title} style={{ width: 120, marginBottom: 8, borderRadius: 5 }} />
                  <div style={{ fontWeight: "bold", fontSize: 16 }}>{item.title}</div>
                </a>
                <div>Price: {item.price}</div>
                {item.brand && <div>Brand: {item.brand}</div>}
                {item.compatibility && <div>Compatibility: {item.compatibility}</div>}
              </div>
            ))}
          </div>
        </div>
      )}
      {/* Existing: Buy / Info Links */}
      {partLinks && !partLinks.error && (
        <div style={{ marginTop: 10 }}>
          <strong>Buy / Info Links:</strong>
          <ul>
            <li>
              <a href={partLinks.google_url} target="_blank" rel="noopener noreferrer">Google Search</a>
            </li>
            <li>
              <a href={partLinks.ebay_url} target="_blank" rel="noopener noreferrer">eBay</a>
            </li>
            <li>
              <a href={partLinks.amazon_url} target="_blank" rel="noopener noreferrer">Amazon</a>
            </li>
          </ul>
        </div>
      )}
      {partLinks?.error && (
        <div style={{ color: 'red', marginTop: 10 }}>{partLinks.error}</div>
      )}
    </div>
  );
}

export default App;

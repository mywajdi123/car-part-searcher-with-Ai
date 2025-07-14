import { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
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
    } catch (err) {
      setResponse({ message: 'Upload failed' });
      console.error(err);
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
        </div>
      )}
    </div>
  );
}

export default App;

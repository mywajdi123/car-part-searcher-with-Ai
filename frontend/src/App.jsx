import { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [message, setMessage] = useState('');
  useEffect(() => {
    axios.get('http://localhost:8000/')
      .then(res => setMessage(res.data.message))
      .catch(() => setMessage('No connection 😢'));
  }, []);
  return <h1>{message}</h1>;
}
export default App;

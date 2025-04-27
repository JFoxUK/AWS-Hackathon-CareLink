import { useState } from 'react';
import axios from 'axios';
import './index.css'; // make sure this is imported!

const API_BASE_URL = '';

function App() {
  const [heartRate, setHeartRate] = useState('');
  const [bloodOxygen, setBloodOxygen] = useState('');
  const [temperature, setTemperature] = useState('');
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submitVitals = async () => {
    try {
      await axios.post(`${API_BASE_URL}/publish-vitals`, {
        device_id: 'carelink-health-monitor',
        heart_rate: parseFloat(heartRate),
        blood_oxygen: parseFloat(bloodOxygen),
        temperature: parseFloat(temperature),
      });
      alert('Vitals published successfully!');
    } catch (error) {
      console.error(error);
      alert('Error publishing vitals');
    }
  };

  const fetchLatestVitals = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/latest-vitals`);
      const resultBody = JSON.parse(response.data.body);
      setAiResult(resultBody);
      setLoading(false);
    } catch (error) {
      console.error(error);
      alert('Error fetching vitals');
      setLoading(false);
    }
  };

  const getRiskLabel = (probability) => {
    if (probability < 0.4) {
      return <span style={{ color: 'green' }}>✅ Stable</span>;
    } else if (probability < 0.7) {
      return <span style={{ color: 'orange' }}>⚠️ Caution</span>;
    } else {
      return <span style={{ color: 'red' }}>❌ Critical</span>;
    }
  };

  return (
    <div className="container">
      <h1>CareLink: Remote Health Monitor</h1>

      <div className="card">
        <h2>Submit Patient Vitals</h2>
        <input type="number" placeholder="Heart Rate (bpm)" value={heartRate} onChange={(e) => setHeartRate(e.target.value)} /><br />
        <input type="number" placeholder="Blood Oxygen (%)" value={bloodOxygen} onChange={(e) => setBloodOxygen(e.target.value)} /><br />
        <input type="number" placeholder="Temperature (°C)" value={temperature} onChange={(e) => setTemperature(e.target.value)} /><br />
        <button onClick={submitVitals} style={{ marginTop: '1rem' }}>
          Submit Vitals
        </button>
      </div>

      <div className="card">
        <h2>Latest Health Analysis</h2>
        <button onClick={fetchLatestVitals}>
          Fetch Latest AI Summary
        </button>

        {loading && <p>Loading...</p>}

        {aiResult && (
          <div className="result-text">
            {aiResult.prediction_probability !== undefined && (
              <p><strong>Status:</strong> {getRiskLabel(aiResult.prediction_probability)}</p>
            )}
            <p><strong>Heart Rate:</strong> {aiResult.heart_rate} bpm</p>
            <p><strong>Blood Oxygen:</strong> {aiResult.blood_oxygen} %</p>
            <p><strong>Temperature:</strong> {aiResult.temperature} °C</p>
            <p><strong>Instability Risk Probability:</strong> {parseFloat(aiResult.prediction_probability).toFixed(3)}</p>
            <p><strong>AI Summary:</strong> {aiResult.alert_summary}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;


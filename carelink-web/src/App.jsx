import { useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Legend,
  Tooltip,
  Title,
} from 'chart.js';
import './App.css';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Legend, Tooltip, Title);

const API_BASE_URL = '';

function App() {
  const [bulkVitals, setBulkVitals] = useState('');
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showInput, setShowInput] = useState(false);

  const submitVitals = async () => {
    try {
      const parsed = JSON.parse(bulkVitals);
      await axios.post(`${API_BASE_URL}/publish-vitals`, {
        device_id: 'carelink-health-monitor',
        vitals: parsed,
      });
      alert('Vitals published successfully!');
    } catch (error) {
      console.error(error);
      alert('Error publishing vitals. Please ensure valid JSON array.');
    }
  };

  const fetchLatestVitals = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/latest-vitals`, {
        params: {
          device_id: 'carelink-health-monitor',
          months_back: 3,
        }
      });
      const resultBody = JSON.parse(response.data.body);
      setAiResult(resultBody);
      setLoading(false);
    } catch (error) {
      console.error(error);
      alert('Error fetching vitals');
      setLoading(false);
    }
  };

  const prepareChartData = () => {
    if (!aiResult || !aiResult.vitals_history) return null;

    const labels = aiResult.vitals_history.map((v) => new Date(v.timestamp).toLocaleString());
    const heartRateData = aiResult.vitals_history.map((v) => v.heart_rate);
    const oxygenData = aiResult.vitals_history.map((v) => v.blood_oxygen);
    const temperatureData = aiResult.vitals_history.map((v) => v.temperature);

    return {
      labels,
      datasets: [
        {
          label: 'Heart Rate (bpm)',
          data: heartRateData,
          borderColor: '#f87171',
          tension: 0.2,
          pointRadius: 0,
          borderWidth: 3,
          fill: false,
        },
        {
          label: 'Blood Oxygen (%)',
          data: oxygenData,
          borderColor: '#60a5fa',
          tension: 0.2,
          pointRadius: 0,
          borderWidth: 3,
          fill: false,
        },
        {
          label: 'Temperature (°C)',
          data: temperatureData,
          borderColor: '#34d399',
          tension: 0.2,
          pointRadius: 0,
          borderWidth: 3,
          fill: false,
        },
      ],
    };
  };

  const renderAIMeter = (score) => {
    const percentage = Math.round(score * 100);
    const color = percentage < 40 ? '#34d399' : percentage < 70 ? '#facc15' : '#f87171';

    return (
      <div className="ai-meter">
        <svg viewBox="0 0 36 36" className="circular-chart">
          <path
            className="circle-bg"
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            className="circle"
            stroke={color}
            strokeDasharray={`${percentage},100`}
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <text x="18" y="20.35" className="percentage" textAnchor="middle" fill={color}>
            {percentage}%
          </text>
        </svg>
        <p style={{ marginTop: '0.5rem', fontWeight: 'bold' }}>Instability Risk</p>
      </div>
    );
  };

  return (
    <div className="container">
      <h1>CareLink: Remote Health Monitor</h1>

      <div className="card small-card">
        <button onClick={() => setShowInput(!showInput)}>
          {showInput ? 'Hide' : 'Show'} Bulk Vitals Input
        </button>

        {showInput && (
          <div className="input-area">
            <textarea
              placeholder="Paste JSON array of vitals here"
              value={bulkVitals}
              onChange={(e) => setBulkVitals(e.target.value)}
              rows={8}
              style={{ width: '100%', fontFamily: 'monospace', marginTop: '1rem' }}
            />
            <button onClick={submitVitals} style={{ marginTop: '1rem' }}>
              Submit Vitals
            </button>
          </div>
        )}
      </div>

      <div className="card">
        <h2>Latest Health Analysis</h2>
        <button onClick={fetchLatestVitals}>Fetch Latest Vitals & AI Summary</button>

        {loading && (
          <div className="spinner-container">
            <div className="loading-spinner"></div>
          </div>
        )}


        {aiResult && (
          <>
            {renderAIMeter(aiResult.sagemaker_prediction)}

            <div className="prediction-score">
              Raw Model Score: {parseFloat(aiResult.sagemaker_prediction).toFixed(5)}
            </div>

            <div className="result-text fade-in">
              <h3>AI Clinical Summary</h3>
              <div className="summary-box">
                {aiResult.bedrock_summary.slice(0, 1200)}
                {aiResult.bedrock_summary.length > 1200 ? '...' : ''}
              </div>
            </div>

            {prepareChartData() && (
              <div className="chart-container">
                <Line
                  data={prepareChartData()}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: { position: 'top' },
                      title: { display: true, text: 'Patient Vitals Over Time' },
                      tooltip: { mode: 'index', intersect: false },
                    },
                    scales: {
                      x: {
                        ticks: {
                          maxTicksLimit: 15,
                          autoSkip: true,
                          maxRotation: 45,
                          minRotation: 0,
                        },
                      },
                      y: {
                        beginAtZero: false,
                      },
                    },
                  }}
                />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;

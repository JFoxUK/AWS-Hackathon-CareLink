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
import { Button } from '@cloudscape-design/components';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Legend, Tooltip, Title);

const API_BASE_URL = 'https://pxn0fm1db2.execute-api.eu-north-1.amazonaws.com/prod';

function HealthMonitor() {
  const [aiResult, setAiResult] = useState(null);
  const [loading, setLoading] = useState(false);

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
      localStorage.setItem('carelink_summary', resultBody.bedrock_summary || '');
      localStorage.setItem('carelink_vitals', JSON.stringify(resultBody.vitals_history || []));
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
      <div>
        <svg viewBox="0 0 36 36" style={{ width: '100px', height: '100px' }}>
          <path
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke="#eee"
            strokeWidth="3"
          />
          <path
            stroke={color}
            strokeDasharray={`${percentage},100`}
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            strokeWidth="3"
          />
          <text x="18" y="20.35" textAnchor="middle" fill={color} style={{ fontSize: '10px' }}>
            {percentage}%
          </text>
        </svg>
        <p style={{ marginTop: '0.5rem', fontWeight: 'bold' }}>Instability Risk</p>
      </div>
    );
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>CareLink: Remote Health Monitor</h1>

      <div style={{ marginBottom: '20px' }}>
        <Button variant="primary" onClick={fetchLatestVitals}>
          Fetch Latest Vitals & AI Summary
        </Button>
      </div>

      {loading && (
        <div>Loading...</div>
      )}

      {/* Most Recent Vitals Card */}
      {aiResult && aiResult.vitals_history && aiResult.vitals_history.length > 0 && (
        <div style={{
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          maxWidth: '400px',
          background: '#fafbfc',
        }}>
          <h3>Most Recent Vitals</h3>
          <div><b>Time:</b> {new Date(aiResult.vitals_history[aiResult.vitals_history.length - 1].timestamp).toLocaleString()}</div>
          <div><b>Heart Rate:</b> {aiResult.vitals_history[aiResult.vitals_history.length - 1].heart_rate} bpm</div>
          <div><b>Blood Oxygen:</b> {aiResult.vitals_history[aiResult.vitals_history.length - 1].blood_oxygen} %</div>
          <div><b>Temperature:</b> {aiResult.vitals_history[aiResult.vitals_history.length - 1].temperature} °C</div>
        </div>
      )}

      {aiResult && (
        <>
          {renderAIMeter(aiResult.sagemaker_prediction)}

          <div style={{ marginTop: '20px' }}>
            Raw Model Score: {parseFloat(aiResult.sagemaker_prediction).toFixed(5)}
          </div>

          <div style={{ marginTop: '20px' }}>
            <h3>AI Clinical Summary</h3>
            <div style={{ 
              padding: '15px', 
              border: '1px solid #ccc', 
              borderRadius: '4px',
              maxHeight: '300px',
              overflowY: 'auto'
            }}>
              {aiResult.bedrock_summary.slice(0, 1200)}
              {aiResult.bedrock_summary.length > 1200 ? '...' : ''}
            </div>
          </div>

          {prepareChartData() && (
            <div style={{ marginTop: '20px', height: '400px' }}>
              <Line
                data={prepareChartData()}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
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
  );
}

export default HealthMonitor; 
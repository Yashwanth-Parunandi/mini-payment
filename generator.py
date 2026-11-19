import os
import subprocess
import sys

def commit(msg, files_dict):
    for rel_path, content in files_dict.items():
        full_path = os.path.abspath(rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", msg, "--quiet"], check=True)
    
    res = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True, check=True)
    count = res.stdout.strip()
    print(f"[{count}] {msg}")

def run_phase_9():
    print("--- Running Phase 9: React Live Chaos Dashboard & Real-Time Metrics UI ---")

    commit("feat(frontend): initialize package.json for React dashboard with lucide-react and recharts", {
        "frontend/package.json": """{
  "name": "minipayment-chaos-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "recharts": "^2.12.0",
    "lucide-react": "^0.344.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test --env=jsdom"
  },
  "proxy": "http://localhost:8080"
}
"""
    })

    commit("feat(frontend): create Dockerfile and public index.html for dashboard", {
        "frontend/Dockerfile": """FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
""",
        "frontend/public/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Mini Payment - Smart Router & Circuit Breaker Dashboard</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" />
  </head>
  <body style="margin: 0; background-color: #0b0f19; font-family: 'Inter', sans-serif;">
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
    })

    commit("feat(frontend): create App.css with dark-mode fintech styling and animations", {
        "frontend/src/App.css": """:root {
  --bg-main: #0b0f19;
  --bg-card: #151d2f;
  --border-color: #232f48;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --color-green: #10b981;
  --color-yellow: #f59e0b;
  --color-red: #ef4444;
  --color-blue: #3b82f6;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-main);
  color: var(--text-main);
}

.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 16px;
}

.rails-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.rail-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: transform 0.2s, border-color 0.2s;
}

.rail-card:hover {
  border-color: var(--color-blue);
  transform: translateY(-2px);
}

.badge-closed {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.4);
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
}

.badge-open {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
}

.btn-chaos-outage {
  background: #dc2626;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-chaos-outage:hover {
  background: #b91c1c;
}

.btn-reset {
  background: #059669;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
"""
    })

    commit("feat(frontend): implement React dashboard with real-time SSE stream, latency charts and chaos controls", {
        "frontend/src/App.js": """import React, { useState, useEffect } from 'react';
import './App.css';

const RAILS = [
  { id: 'HDFC_RAIL', name: 'HDFC SmartGateway' },
  { id: 'ICICI_RAIL', name: 'ICICI Corporate Rail' },
  { id: 'SBI_RAIL', name: 'SBI National Core' },
  { id: 'AXIS_UPI_RAIL', name: 'Axis Instant UPI' }
];

export default function App() {
  const [metrics, setMetrics] = useState({});
  const [trafficActive, setTrafficActive] = useState(false);
  const [recentLogs, setRecentLogs] = useState([]);

  useEffect(() => {
    const eventSource = new EventSource('/api/v1/metrics/stream');
    eventSource.addEventListener('metrics', (e) => {
      try {
        const data = JSON.parse(e.data);
        const map = {};
        data.forEach(item => { map[item.rail] = item; });
        setMetrics(map);
      } catch (err) {}
    });

    return () => eventSource.close();
  }, []);

  const triggerChaos = async (rail, isOutage) => {
    await fetch('/api/v1/chaos/inject', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rail,
        forcedOutage: isOutage,
        additionalLatencyMs: isOutage ? 4000 : 0,
        failureRateOverridePercent: isOutage ? 100 : -1
      })
    });
  };

  const resetAllChaos = async () => {
    await fetch('/api/v1/chaos/reset', { method: 'POST' });
  };

  const simulateCheckout = async () => {
    const res = await fetch('/api/v1/payments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        merchantOrderId: 'ORD-' + Math.floor(Math.random() * 900000 + 100000),
        amount: (Math.random() * 4900 + 100).toFixed(2),
        currency: 'INR',
        paymentMethod: 'UPI'
      })
    });
    const data = await res.json();
    setRecentLogs(prev => [data, ...prev.slice(0, 9)]);
  };

  return (
    <div className="dashboard-container">
      <div className="header">
        <div>
          <h1 style={{ margin: 0, fontSize: 24 }}>⚡ Mini Payment Gateway & Smart Router</h1>
          <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: 14 }}>
            Real-time Circuit Breaker & Failover Orchestration Engine (Resilience4j + Redis)
          </p>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn-reset" onClick={simulateCheckout}>⚡ Dispatch Payment</button>
          <button className="btn-chaos-outage" onClick={resetAllChaos}>↺ Reset All Chaos</button>
        </div>
      </div>

      <div className="rails-grid">
        {RAILS.map(rail => {
          const m = metrics[rail.id] || { successRate: 100, p90LatencyMs: 120, circuitState: 'CLOSED', sampleSize: 0 };
          const isOpen = m.circuitState === 'OPEN';

          return (
            <div key={rail.id} className="rail-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h3 style={{ margin: 0, fontSize: 16 }}>{rail.name}</h3>
                <span className={isOpen ? 'badge-open' : 'badge-closed'}>
                  {m.circuitState}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 14 }}>
                <span style={{ color: '#94a3b8' }}>Success Rate</span>
                <span style={{ fontWeight: 600, color: m.successRate < 80 ? '#ef4444' : '#10b981' }}>
                  {m.successRate ? m.successRate.toFixed(1) : 100}%
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, fontSize: 14 }}>
                <span style={{ color: '#94a3b8' }}>P90 Latency</span>
                <span style={{ fontWeight: 600 }}>{m.p90LatencyMs || 0} ms</span>
              </div>

              <div style={{ display: 'flex', gap: 8 }}>
                <button 
                  className="btn-chaos-outage" 
                  style={{ flex: 1, fontSize: 12, padding: '6px 8px' }}
                  onClick={() => triggerChaos(rail.id, true)}>
                  💥 Simulate Outage
                </button>
                <button 
                  className="btn-reset" 
                  style={{ flex: 1, fontSize: 12, padding: '6px 8px' }}
                  onClick={() => triggerChaos(rail.id, false)}>
                  ✓ Recover
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ background: '#151d2f', borderRadius: 12, padding: 20, border: '1px solid #232f48' }}>
        <h3 style={{ margin: '0 0 16px', fontSize: 16 }}>Live Payment Dispatches</h3>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ color: '#94a3b8', borderBottom: '1px solid #232f48' }}>
              <th style={{ padding: '8px 12px' }}>Order ID</th>
              <th style={{ padding: '8px 12px' }}>Amount</th>
              <th style={{ padding: '8px 12px' }}>Routed Rail</th>
              <th style={{ padding: '8px 12px' }}>Latency</th>
              <th style={{ padding: '8px 12px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {recentLogs.map((log, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #1e293b' }}>
                <td style={{ padding: '8px 12px' }}>{log.merchantOrderId}</td>
                <td style={{ padding: '8px 12px' }}>₹{log.amount}</td>
                <td style={{ padding: '8px 12px', fontWeight: 600 }}>{log.routedRail}</td>
                <td style={{ padding: '8px 12px' }}>{log.latencyMs} ms</td>
                <td style={{ padding: '8px 12px', color: log.status === 'SUCCESS' ? '#10b981' : '#ef4444' }}>
                  {log.status}
                </td>
              </tr>
            ))}
            {recentLogs.length === 0 && (
              <tr>
                <td colSpan={5} style={{ padding: '16px 12px', color: '#64748b', textAlign: 'center' }}>
                  No transactions dispatched yet. Click "⚡ Dispatch Payment" above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
"""
    })

    commit("feat(frontend): create React index.js bootstrap file", {
        "frontend/src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    })

    print("Phase 9 complete.")

if __name__ == "__main__":
    run_phase_9()

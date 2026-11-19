import React, { useState, useEffect } from 'react';
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

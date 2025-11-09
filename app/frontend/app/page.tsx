'use client'

import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [status, setStatus] = useState<any>(null)
  const [metrics, setMetrics] = useState<any>(null)

  useEffect(() => {
    // Fetch status
    fetch('http://localhost:8080/api/status')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error('Failed to fetch status:', err))

    // Fetch metrics
    fetch('http://localhost:8080/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error('Failed to fetch metrics:', err))
  }, [])

  return (
    <main className="min-h-screen bg-gray-100 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">NexiTrade Dashboard</h1>
        
        {/* Status Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">System Status</h2>
          {status ? (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className="text-lg font-medium">{status.status}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Mode</p>
                <p className="text-lg font-medium">{status.mode}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Can Trade</p>
                <p className="text-lg font-medium">{status.can_trade ? 'Yes' : 'No'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Circuit Breaker</p>
                <p className="text-lg font-medium">
                  {status.circuit_breaker_triggered ? 'Triggered' : 'Normal'}
                </p>
              </div>
            </div>
          ) : (
            <p>Loading...</p>
          )}
        </div>

        {/* Metrics Card */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Performance Metrics</h2>
          {metrics ? (
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-500">Sharpe Ratio</p>
                <p className="text-2xl font-bold">{metrics.sharpe_ratio?.toFixed(2) || '0.00'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Max Drawdown</p>
                <p className="text-2xl font-bold text-red-500">
                  {(metrics.max_drawdown * 100)?.toFixed(2) || '0.00'}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Return</p>
                <p className="text-2xl font-bold text-green-500">
                  {(metrics.total_return * 100)?.toFixed(2) || '0.00'}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Win Rate</p>
                <p className="text-2xl font-bold">
                  {(metrics.win_rate * 100)?.toFixed(1) || '0.0'}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Trades</p>
                <p className="text-2xl font-bold">{metrics.num_trades || 0}</p>
              </div>
            </div>
          ) : (
            <p>Loading...</p>
          )}
        </div>

        {/* Emergency Stop */}
        <div className="mt-6">
          <button
            onClick={() => {
              if (confirm('Are you sure you want to activate the kill switch?')) {
                fetch('http://localhost:8080/api/kill', { method: 'POST' })
                  .then(res => res.json())
                  .then(data => alert(data.message))
                  .catch(err => alert('Failed to activate kill switch'))
              }
            }}
            className="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg"
          >
            🛑 EMERGENCY STOP (Kill Switch)
          </button>
        </div>
      </div>
    </main>
  )
}


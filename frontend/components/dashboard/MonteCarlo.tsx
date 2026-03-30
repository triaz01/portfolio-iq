'use client'
import { useState, useEffect } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { runMonteCarlo } from '@/lib/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function MonteCarlo() {
  const { metrics } = useAppStore()
  const [years, setYears] = useState(20)
  const [withdrawal, setWithdrawal] = useState(0)
  const [mcData, setMcData] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (metrics) {
      setLoading(true)
      runMonteCarlo({
        initial_value: (metrics as any).total_value,
        cagr: (metrics as any).annualized_return,
        volatility: (metrics as any).annual_volatility,
        years,
        simulations: 500,
        annual_withdrawal: withdrawal
      }).then(data => {
        // Convert object to array for Recharts
        const chartData = Object.entries(data.data).map(([year, values]: [string, any]) => ({
          year: parseFloat(year),
          'Bear Market (10th)': values['10th Percentile (Bear Market)'],
          'Expected (50th)': values['50th Percentile (Expected)'],
          'Bull Market (90th)': values['90th Percentile (Bull Market)']
        }))
        setMcData(chartData)
        setLoading(false)
      }).catch(() => {
        setLoading(false)
      })
    }
  }, [metrics, years, withdrawal])

  if (!metrics) return null

  return (
    <div className="bg-white" 
      style={{
        border: '1px solid #e2e8f0',
        borderTop: '4px solid #1a6e4a',
        boxShadow: '0 2px 8px rgba(13,17,23,0.05)',
        borderRadius: '20px',
        padding: '28px',
        marginBottom: '28px'
      }}>
      <div style={{ borderBottom: '1px solid #f1f5f9', padding: '24px 28px', marginBottom: '20px', marginLeft: '-28px', marginRight: '-28px', marginTop: '-28px' }}>
        <div className="flex items-center gap-3">
          <div 
            style={{
              width: '42px',
              height: '42px',
              borderRadius: '11px',
              background: '#dcfce7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              marginRight: '14px'
            }}>
            <span style={{ fontSize: '20px' }}>🎲</span>
          </div>
          <div>
            <div style={{
              fontFamily: 'DM Serif Display, Georgia, serif',
              fontSize: '19px',
              fontWeight: '700',
              color: '#0d1117',
              letterSpacing: '-0.3px'
            }}>
              Monte Carlo Simulation
            </div>
            <div style={{
              fontFamily: 'Arial',
              fontSize: '14px',
              color: '#94a3b8',
              marginTop: '3px'
            }}>
              500 scenarios based on your portfolio risk/return profile
            </div>
          </div>
        </div>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr 1fr', 
        gap: '24px', 
        marginBottom: '24px' 
      }}>
        <div>
          <label style={{
            display: 'block',
            fontFamily: 'Arial, sans-serif',
            fontSize: '15px',
            color: '#3a4150',
            marginBottom: '10px'
          }}>
            Projection Horizon <span style={{ fontWeight: 'bold', color: '#2556a0' }}>{years} years</span>
          </label>
          <input
            type="range"
            min="5"
            max="30"
            value={years}
            onChange={e => setYears(Number(e.target.value))}
            style={{
              width: '100%',
              accentColor: '#1a3d6e'
            }}
          />
        </div>
        <div>
          <label style={{
            display: 'block',
            fontFamily: 'Arial, sans-serif',
            fontSize: '15px',
            color: '#3a4150',
            marginBottom: '10px'
          }}>
            Annual Withdrawal ($)
          </label>
          <input
            type="number"
            min="0"
            step="5000"
            value={withdrawal}
            onChange={e => setWithdrawal(Number(e.target.value))}
            style={{
              width: '100%',
              border: '1.5px solid #e2e8f0',
              borderRadius: '8px',
              padding: '9px 12px',
              fontSize: '15px',
              fontFamily: 'Arial, sans-serif',
              height: '44px'
            }}
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-ink-muted">
          Running simulations...
        </div>
      ) : mcData ? (
        <>
          <div className="h-80" style={{ minHeight: '320px' }}>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={mcData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="year" 
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                  stroke="#e2e8f0"
                  label={{ value: 'Years', position: 'insideBottom', offset: -5, style: { fontSize: 12, fill: '#94a3b8' } }}
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#94a3b8' }}
                  stroke="#e2e8f0"
                  tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
                />
                <Tooltip 
                  formatter={(value: any) => [`$${(value / 1000000).toFixed(2)}M`, '']}
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px'
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '13px' }} />
                <Line 
                  type="monotone" 
                  dataKey="Bear Market (10th)" 
                  stroke="#dc2626" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="Expected (50th)" 
                  stroke="#2556a0" 
                  strokeWidth={3}
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="Bull Market (90th)" 
                  stroke="#1a6e4a" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div style={{
            marginTop: '16px',
            fontSize: '13px',
            color: '#94a3b8',
            fontStyle: 'italic',
            fontFamily: 'Arial, sans-serif',
            lineHeight: '1.7'
          }}>
            This Monte Carlo simulation projects 500 possible portfolio outcomes based on your current holdings' historical return and volatility. 
            Results represent statistical probabilities, not guarantees. Past performance does not predict future results. 
            Actual outcomes may vary significantly due to market conditions, economic factors, and individual circumstances.
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-ink-muted">
          Unable to run simulation
        </div>
      )}
    </div>
  )
}

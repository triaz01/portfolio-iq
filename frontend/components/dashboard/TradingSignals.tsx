'use client'
import { useAppStore } from '@/store/useAppStore'

export default function TradingSignals() {
  const { signals } = useAppStore()

  if (!signals) return null

  return (
    <div className="bg-white" 
      style={{
        border: '1px solid #e2e8f0',
        borderTop: '4px solid #1a3d6e',
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
              background: '#dbeafe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              marginRight: '14px'
            }}>
            <span style={{ fontSize: '20px' }}>⚡</span>
          </div>
          <div>
            <div style={{
              fontFamily: 'DM Serif Display, Georgia, serif',
              fontSize: '19px',
              fontWeight: '700',
              color: '#0d1117',
              letterSpacing: '-0.3px'
            }}>
              Trading Signals
            </div>
            <div style={{
              fontFamily: 'Arial',
              fontSize: '14px',
              color: '#94a3b8',
              marginTop: '3px'
            }}>
              Momentum, trend, and relative strength analysis
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '15px',
          fontFamily: 'Arial'
        }}>
          <thead>
            <tr>
              <th style={{
                background: '#f8fafc',
                padding: '13px 16px',
                fontSize: '13px',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                color: '#94a3b8',
                borderBottom: '2px solid #e2e8f0',
                textAlign: 'left'
              }}>Ticker</th>
              <th style={{
                background: '#f8fafc',
                padding: '13px 16px',
                fontSize: '12px',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                color: '#94a3b8',
                borderBottom: '2px solid #e2e8f0',
                textAlign: 'right'
              }}>Momentum</th>
              <th style={{
                background: '#f8fafc',
                padding: '13px 16px',
                fontSize: '12px',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                color: '#94a3b8',
                borderBottom: '2px solid #e2e8f0',
                textAlign: 'right'
              }}>200DMA Trend</th>
              <th style={{
                background: '#f8fafc',
                padding: '13px 16px',
                fontSize: '12px',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                color: '#94a3b8',
                borderBottom: '2px solid #e2e8f0',
                textAlign: 'right'
              }}>Rel Strength</th>
              <th style={{
                background: '#f8fafc',
                padding: '13px 16px',
                fontSize: '12px',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                color: '#94a3b8',
                borderBottom: '2px solid #e2e8f0',
                textAlign: 'center'
              }}>Total Score</th>
              <th style={{
                background: '#f8fafc',
                padding: '13px 16px',
                fontSize: '12px',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                color: '#94a3b8',
                borderBottom: '2px solid #e2e8f0',
                textAlign: 'center'
              }}>Recommendation</th>
            </tr>
          </thead>
          <tbody>
            {signals.map((signal: any, i: number) => {
              const isLastRow = i === signals.length - 1
              const getRecommendationStyle = (rec: string) => {
                if (rec === 'Buy') {
                  return {
                    background: '#dcfce7',
                    color: '#166534',
                    fontWeight: '700'
                  }
                } else if (rec === 'Hold') {
                  return {
                    background: '#fef9c3',
                    color: '#854d0e',
                    fontWeight: '700'
                  }
                } else if (rec === 'Sell / Avoid') {
                  return {
                    background: '#fee2e2',
                    color: '#991b1b',
                    fontWeight: '700'
                  }
                }
                return {
                  background: '#f3f4f6',
                  color: '#6b7280',
                  fontWeight: '700'
                }
              }
              
              return (
                <tr key={i}
                  style={{
                    verticalAlign: 'middle'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.background = '#f8fafc'
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = 'transparent'
                  }}>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    fontFamily: 'monospace'
                  }}>{signal.Ticker}</td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'right'
                  }}>
                    {signal['Momentum (%)'] !== 'N/A' ? `${signal['Momentum (%)']}%` : 'N/A'}
                  </td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'right'
                  }}>
                    {signal['Trend vs 200DMA (%)'] !== 'N/A' ? `${signal['Trend vs 200DMA (%)']}%` : 'N/A'}
                  </td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'right'
                  }}>
                    {signal['Rel Strength vs SPY (%)'] !== 'N/A' ? `${signal['Rel Strength vs SPY (%)']}%` : 'N/A'}
                  </td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'center',
                    fontFamily: 'monospace',
                    fontWeight: 'bold'
                  }}>
                    {signal['Total Score'] !== 'N/A' ? signal['Total Score'] : 'N/A'}
                  </td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'center'
                  }}>
                    <span style={{
                      ...getRecommendationStyle(signal.Recommendation),
                      padding: '3px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      display: 'inline-block'
                    }}>
                      {signal.Recommendation}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

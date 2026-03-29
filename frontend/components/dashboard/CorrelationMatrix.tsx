'use client'
import { useAppStore } from '@/lib/useAppStore'

export default function CorrelationMatrix() {
  const { correlationMatrix } = useAppStore()

  if (!correlationMatrix) return null

  const tickers = Object.keys(correlationMatrix)
  
  return (
    <div className="bg-white" 
      style={{
        border: '1px solid #e2e8f0',
        borderTop: '4px solid #64748b',
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
              background: '#f1f5f9',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              marginRight: '14px'
            }}>
            <span style={{ fontSize: '20px' }}>🔗</span>
          </div>
          <div>
            <div style={{
              fontFamily: 'DM Serif Display, Georgia, serif',
              fontSize: '19px',
              fontWeight: '700',
              color: '#0d1117',
              letterSpacing: '-0.3px'
            }}>
              Correlation Matrix
            </div>
            <div style={{
              fontFamily: 'Arial',
              fontSize: '14px',
              color: '#94a3b8',
              marginTop: '3px'
            }}>
              Portfolio diversification analysis
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-base">
          <thead>
            <tr>
              <th className="py-2 px-3"></th>
              {tickers.map(ticker => (
                <th key={ticker} className="py-2 px-3 font-mono text-sm font-semibold text-ink-soft">
                  {ticker}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {tickers.map(rowTicker => (
              <tr key={rowTicker}>
                <td className="py-2 px-3 font-mono text-sm font-semibold text-ink">
                  {rowTicker}
                </td>
                {tickers.map(colTicker => {
                  const correlation = (correlationMatrix as any)[rowTicker][colTicker]
                  const intensity = Math.abs(correlation)
                  const bgColor = correlation > 0.7 
                    ? `rgba(220, 38, 38, ${intensity * 0.3})`
                    : correlation < -0.7
                    ? `rgba(26, 110, 74, ${intensity * 0.3})`
                    : intensity > 0.3
                    ? `rgba(201, 148, 58, ${intensity * 0.2})`
                    : 'transparent'
                  
                  return (
                    <td 
                      key={colTicker}
                      className="py-2 px-3 text-center font-mono"
                      style={{ backgroundColor: bgColor }}
                    >
                      <span className={correlation > 0.7 ? 'text-red-600' : correlation < -0.7 ? 'text-green-600' : 'text-ink'}>
                        {correlation.toFixed(2)}
                      </span>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

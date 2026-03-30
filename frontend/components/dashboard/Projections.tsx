'use client'
import { useAppStore } from '@/store/useAppStore'

export default function Projections() {
  const { projectionDf, metrics } = useAppStore()

  if (!projectionDf) return null

  // Calculate totals
  const totalCurrentValue = projectionDf.reduce((sum, row: any) => sum + (row['Current Value'] || 0), 0)
  const totalProjectedValue = projectionDf.reduce((sum, row: any) => sum + (row['Projected Value'] || 0), 0)
  const totalUpside = totalCurrentValue > 0 ? ((totalProjectedValue - totalCurrentValue) / totalCurrentValue) * 100 : 0

  return (
    <div className="bg-white" 
      style={{
        border: '1px solid #e2e8f0',
        borderTop: '4px solid #c9943a',
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
              background: '#fef3c7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              marginRight: '14px'
            }}>
            <span style={{ fontSize: '20px' }}>🔮</span>
          </div>
          <div>
            <div style={{
              fontFamily: 'DM Serif Display, Georgia, serif',
              fontSize: '19px',
              fontWeight: '700',
              color: '#0d1117',
              letterSpacing: '-0.3px'
            }}>
              Analyst Projections
            </div>
            <div style={{
              fontFamily: 'Arial',
              fontSize: '14px',
              color: '#94a3b8',
              marginTop: '3px'
            }}>
              Current vs target prices and projected values
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
              }}>Shares</th>
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
              }}>Current Price</th>
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
              }}>Target Price</th>
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
              }}>Upside %</th>
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
              }}>Current Value</th>
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
              }}>Projected Value</th>
            </tr>
          </thead>
          <tbody>
            {projectionDf.map((row: any, i: number) => {
              const upsidePercent = ((row['Target Price'] / row['Current Price']) - 1) * 100
              const isLastRow = i === projectionDf.length - 1
              const isFallbackTarget = row['Target Source'] === 'fallback' || row['Target Source'] === 'error_fallback'
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
                  }}>{row.Ticker}</td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'right'
                  }}>{row.Shares.toLocaleString()}</td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'right'
                  }}>${row['Current Price'].toFixed(2)}</td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'right'
                  }}>${row['Target Price'].toFixed(2)}</td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: isFallbackTarget ? '#94a3b8' : (upsidePercent > 0 ? '#1a6e4a' : upsidePercent < 0 ? '#dc2626' : '#3a4150'),
                    fontWeight: 'bold',
                    textAlign: 'right'
                  }}>
                    {isFallbackTarget ? 'N/A' : `${upsidePercent.toFixed(1)}%`}
                  </td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    textAlign: 'right'
                  }}>${row['Current Value'].toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}</td>
                  <td style={{
                    padding: '14px 16px',
                    lineHeight: '1.5',
                    borderBottom: isLastRow ? 'none' : '1px solid #f1f5f9',
                    color: '#3a4150',
                    fontWeight: 'bold',
                    textAlign: 'right'
                  }}>${row['Projected Value'].toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Summary Section */}
      <div style={{
        marginTop: '24px',
        padding: '20px',
        background: '#fef3c7',
        borderRadius: '12px',
        border: '1px solid #f59e0b'
      }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px'
        }}>
          <div>
            <div style={{
              fontSize: '12px',
              color: '#92400e',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '4px'
            }}>
              Total Current Value
            </div>
            <div style={{
              fontSize: '20px',
              fontWeight: '700',
              color: '#1a3d6e',
              fontFamily: 'Arial'
            }}>
              ${totalCurrentValue.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}
            </div>
          </div>
          
          <div>
            <div style={{
              fontSize: '12px',
              color: '#92400e',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '4px'
            }}>
              Total Projected Value
            </div>
            <div style={{
              fontSize: '20px',
              fontWeight: '700',
              color: '#1a3d6e',
              fontFamily: 'Arial'
            }}>
              ${totalProjectedValue.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}
            </div>
          </div>
          
          <div>
            <div style={{
              fontSize: '12px',
              color: '#92400e',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '4px'
            }}>
              Total Projected Upside
            </div>
            <div style={{
              fontSize: '20px',
              fontWeight: '700',
              color: totalUpside > 0 ? '#1a6e4a' : totalUpside < 0 ? '#dc2626' : '#3a4150',
              fontFamily: 'Arial'
            }}>
              {totalUpside > 0 ? '+' : ''}{totalUpside.toFixed(1)}%
            </div>
          </div>
        </div>

        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: 'rgba(255, 255, 255, 0.7)',
          borderRadius: '8px',
          fontSize: '12px',
          color: '#78716c',
          lineHeight: '1.5'
        }}>
          <strong>Analysis:</strong> Based on {projectionDf.length} holdings, analyst price targets project a total upside of {totalUpside.toFixed(1)}% across the portfolio. 
          {totalUpside > 0 
            ? ` This represents a potential increase of $${(totalProjectedValue - totalCurrentValue).toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})} from current levels.`
            : ' Current projections suggest consolidation may be needed.'
          }
        </div>
      </div>
    </div>
  )
}

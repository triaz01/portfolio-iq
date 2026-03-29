'use client'
import { useAppStore } from '@/lib/useAppStore'

export default function StatGrid() {
  const { metrics } = useAppStore()

  if (!metrics) return null

  const stats = [
    {
      label: 'Annual Return',
      value: `${((metrics as any).annualized_return * 100).toFixed(2)}%`,
      color: '#1a6e4a',
      subLabel: 'Per year'
    },
    {
      label: 'Volatility',
      value: `${((metrics as any).annual_volatility * 100).toFixed(2)}%`,
      color: '#1a3d6e',
      subLabel: 'Annualized'
    },
    {
      label: 'Max Drawdown',
      value: `${((metrics as any).max_drawdown * 100).toFixed(2)}%`,
      color: '#dc2626',
      subLabel: 'Peak to trough'
    },
    {
      label: 'Dividend Yield',
      value: `${((metrics as any).weighted_dividend_yield * 100).toFixed(2)}%`,
      color: '#c9943a',
      subLabel: 'Annual payout'
    },
    {
      label: 'Portfolio Beta',
      value: ((metrics as any).portfolio_beta).toFixed(2),
      color: '#2556a0',
      subLabel: 'Market sensitivity'
    }
  ]

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
            <span style={{ fontSize: '20px' }}>📊</span>
          </div>
          <div>
            <div style={{
              fontFamily: 'DM Serif Display, Georgia, serif',
              fontSize: '19px',
              fontWeight: '700',
              color: '#0d1117',
              letterSpacing: '-0.3px'
            }}>
              Performance Metrics
            </div>
            <div style={{
              fontFamily: 'Arial',
              fontSize: '14px',
              color: '#94a3b8',
              marginTop: '3px'
            }}>
              Key performance indicators
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '14px', marginBottom: '14px' }}>
        {stats.map((stat, i) => (
          <div key={i} 
            style={{
              background: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '14px',
              padding: '20px 18px',
              borderLeft: `3px solid ${stat.color}`
            }}>
            <div style={{
              fontFamily: 'Arial',
              fontSize: '13px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              color: '#94a3b8',
              marginBottom: '8px'
            }}>
              {stat.label}
            </div>
            <div style={{
              fontFamily: 'DM Serif Display',
              fontSize: '32px',
              letterSpacing: '-0.5px',
              lineHeight: '1',
              color: stat.color,
              marginBottom: '8px'
            }}>
              {stat.value}
            </div>
            <div style={{
              fontFamily: 'Arial',
              fontSize: '13px',
              color: '#94a3b8'
            }}>
              {stat.subLabel}
            </div>
          </div>
        ))}
      </div>

      <div style={{
        background: '#f8fafc',
        borderLeft: '4px solid #1a3d6e',
        borderRadius: '10px',
        padding: '20px 24px',
        marginTop: '14px'
      }}>
        <div style={{
          fontFamily: 'Arial',
          fontSize: '16px',
          color: '#475569',
          lineHeight: '1.8'
        }}>
          Your portfolio demonstrates {((metrics as any).annualized_return > 0 ? 'positive' : 'negative')} performance with an annualized return of {((metrics as any).annualized_return * 100).toFixed(2)}% and volatility of {((metrics as any).annual_volatility * 100).toFixed(2)}%. The maximum drawdown of {Math.abs((metrics as any).max_drawdown * 100).toFixed(2)}% indicates {Math.abs((metrics as any).max_drawdown) < 0.2 ? 'moderate' : 'significant'} risk exposure. With a beta of {((metrics as any).portfolio_beta).toFixed(2)}, your portfolio exhibits {((metrics as any).portfolio_beta > 1 ? 'higher' : ((metrics as any).portfolio_beta < 1 ? 'lower' : 'market'))} sensitivity to market movements compared to the broader market.
        </div>
      </div>
    </div>
  )
}

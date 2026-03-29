'use client'

const cards = [
  {
    num: '01',
    title: 'IPS-Driven Analysis',
    body: "Every metric, target, and alert is calibrated to your client's Investment Policy Statement — not generic benchmarks.",
    accent: '#1a3d6e',
    light: '#dbeafe',
    numColor: '#1a3d6e',
  },
  {
    num: '02',
    title: 'Institutional Risk Tools',
    body: 'Volatility, beta, correlation matrix, drawdown, Monte Carlo simulations — the same toolkit used by professional portfolio managers.',
    accent: '#c9943a',
    light: '#fef3c7',
    numColor: '#c9943a',
  },
  {
    num: '03',
    title: 'Client-Ready in Minutes',
    body: 'Input tickers, answer 5 questions, download a branded PDF tear sheet. From blank screen to client presentation in under 3 minutes.',
    accent: '#1a6e4a',
    light: '#dcfce7',
    numColor: '#1a6e4a',
  },
]

export default function USPCards() {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 20,
      marginBottom: 40,
    }}>
      {cards.map(c => (
        <div
          key={c.title}
          style={{
            background: '#ffffff',
            border: '1px solid #e2e8f0',
            borderRadius: 16,
            padding: '32px 28px',
            position: 'relative',
            overflow: 'hidden',
            transition: 'transform 0.2s, box-shadow 0.2s',
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)'
            ;(e.currentTarget as HTMLElement).style.boxShadow = '0 8px 24px rgba(13,17,23,0.08)'
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLElement).style.transform = 'translateY(0)'
            ;(e.currentTarget as HTMLElement).style.boxShadow = 'none'
          }}
        >
          {/* accent bar top */}
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0,
            height: 4,
            background: c.accent,
            borderRadius: '16px 16px 0 0',
          }} />

          {/* large number */}
          <div style={{
            fontFamily: "'DM Serif Display', Georgia, serif",
            fontSize: 48,
            fontWeight: 700,
            color: c.accent,
            lineHeight: 1,
            marginBottom: 16,
            marginTop: 8,
            letterSpacing: '-2px',
          }}>
            {c.num}
          </div>

          <div style={{
            fontFamily: "'DM Serif Display', Georgia, serif",
            fontSize: 18,
            fontWeight: 700,
            color: '#0d1117',
            marginBottom: 12,
            lineHeight: 1.25,
            letterSpacing: '-0.3px',
          }}>
            {c.title}
          </div>

          <div style={{
            fontSize: 14,
            color: '#64748b',
            lineHeight: 1.75,
            fontFamily: 'Arial, sans-serif',
          }}>
            {c.body}
          </div>
        </div>
      ))}
    </div>
  )
}

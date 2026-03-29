export default function Hero() {
  return (
    <div style={{
      background: 'linear-gradient(150deg, #1a3d6e 0%, #0a1f3d 100%)',
      borderRadius: 24,
      padding: '72px 64px 60px 64px',
      marginBottom: 32,
      position: 'relative',
      overflow: 'hidden',
    }}>

      {/* dot pattern */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)',
        backgroundSize: '28px 28px',
        pointerEvents: 'none',
      }} />

      <div style={{ position: 'relative', zIndex: 2 }}>

        {/* Badge */}
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          background: 'rgba(255,255,255,0.10)',
          border: '1px solid rgba(255,255,255,0.22)',
          borderRadius: 30,
          padding: '6px 16px',
          marginBottom: 28,
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: '1.2px',
          textTransform: 'uppercase' as const,
          color: '#ffffff',
          fontFamily: 'Arial, sans-serif',
        }}>
          <span style={{
            width: 7, height: 7,
            borderRadius: '50%',
            background: '#4ade80',
            display: 'inline-block',
            flexShrink: 0,
          }} />
          Built for Financial Advisors
        </div>

        {/* H1 */}
        <div style={{
          fontFamily: "'DM Serif Display', Georgia, serif",
          fontSize: 'clamp(36px, 4vw, 56px)',
          lineHeight: 1.08,
          letterSpacing: '-1.5px',
          color: '#ffffff',
          fontWeight: 700,
          margin: '0 0 20px 0',
        }}>
          Institutional-Grade Portfolio Analysis,{' '}
          <br />
          <span style={{
            fontStyle: 'italic',
            color: '#7ab8f5',
            fontWeight: 400,
          }}>
            in minutes.
          </span>
        </div>

        {/* Subtitle */}
        <div style={{
          fontSize: 18,
          fontWeight: 300,
          lineHeight: 1.75,
          color: '#a8c4e0',
          margin: '0 0 44px 0',
          maxWidth: 620,
          fontFamily: 'Arial, sans-serif',
        }}>
          Generate a personalized IPS, analyze portfolio risk,
          run Monte Carlo stress tests, and export a
          client-ready PDF report — all in one workflow.
        </div>

        {/* Steps */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap' as const,
          alignItems: 'center',
          gap: 0,
          marginBottom: 44,
        }}>
          {[
            ['1', 'Define IPS', 'Goals & risk profile'],
            ['2', 'Analyze Portfolio', 'Risk, corelation, buy/sell signals'],
            ['3', 'Stress Test', 'Growth projection and simulation'],
          ].map(([num, title, sub], i, arr) => (
            <div
              key={num}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 14,
                paddingRight: i < arr.length - 1 ? 36 : 0,
                marginRight: i < arr.length - 1 ? 36 : 0,
                borderRight: i < arr.length - 1
                  ? '1px solid rgba(255,255,255,0.15)'
                  : 'none',
              }}
            >
              <div style={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                background: '#2556a0',
                border: '2px solid rgba(255,255,255,0.35)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 15,
                fontWeight: 800,
                color: '#ffffff',
                flexShrink: 0,
                fontFamily: 'Arial, sans-serif',
              }}>
                {num}
              </div>
              <div>
                <div style={{
                  fontSize: 15,
                  fontWeight: 700,
                  color: '#ffffff',
                  marginBottom: 3,
                  fontFamily: 'Arial, sans-serif',
                }}>
                  {title}
                </div>
                <div style={{
                  fontSize: 14,
                  color: '#7aa5cc',
                  fontFamily: 'Arial, sans-serif',
                }}>
                  {sub}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Trust strip */}
        <div style={{
          display: 'flex',
          flexWrap: 'wrap' as const,
          gap: 24,
          paddingTop: 28,
          borderTop: '1px solid rgba(255,255,255,0.12)',
          fontSize: 15,
          fontWeight: 500,
          color: '#7aa5cc',
          fontFamily: 'Arial, sans-serif',
        }}>
          {[
            'IPS-aligned analysis',
            'Canadian & US stocks',
            'Rules-based trade signals',
          ].map((t, i, arr) => (
            <span key={t}>
              ✓ {t}
              {i < arr.length - 1 && (
                <span style={{
                  margin: '0 12px',
                  color: 'rgba(255,255,255,0.3)',
                  fontSize: 16,
                }}>
                  •
                </span>
              )}
            </span>
          ))}
        </div>

      </div>
    </div>
  )
}

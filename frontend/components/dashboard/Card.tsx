import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  accent?: string
  style?: React.CSSProperties
}

export function Card({ children, accent, style }: CardProps) {
  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e2e8f0',
      borderRadius: 20,
      overflow: 'hidden',
      boxShadow: '0 2px 8px rgba(13,17,23,0.05)',
      marginBottom: 28,
      ...(accent ? { borderTop: `4px solid ${accent}` } : {}),
      ...style,
    }}>
      {children}
    </div>
  )
}

export function CardHeader({
  icon, iconBg, title, sub, right,
}: {
  icon: string
  iconBg: string
  title: string
  sub?: string
  right?: ReactNode
}) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '24px 28px 20px 28px',
      borderBottom: '1px solid #f1f5f9',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 14,
      }}>
        <div style={{
          width: 42, height: 42,
          borderRadius: 11,
          background: iconBg,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 20,
          flexShrink: 0,
        }}>
          {icon}
        </div>
        <div>
          <div style={{
            fontFamily: "'DM Serif Display', Georgia, serif",
            fontSize: 19,
            fontWeight: 700,
            color: '#0d1117',
            letterSpacing: '-0.3px',
          }}>
            {title}
          </div>
          {sub && (
            <div style={{
              fontSize: 13,
              color: '#94a3b8',
              fontFamily: 'Arial, sans-serif',
              marginTop: 3,
            }}>
              {sub}
            </div>
          )}
        </div>
      </div>
      {right && <div>{right}</div>}
    </div>
  )
}

export function CardBody({
  children,
  style,
}: {
  children: ReactNode
  style?: React.CSSProperties
}) {
  return (
    <div style={{ padding: 28, ...style }}>
      {children}
    </div>
  )
}

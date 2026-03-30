'use client'
import { useState, useEffect } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { checkAlignment } from '@/lib/api'

export default function IPSAlignment() {
  const { metrics, ipsTargets, ipsProfile } = useAppStore()
  const [alignment, setAlignment] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (metrics && ipsTargets && ipsProfile) {
      setLoading(true)
      checkAlignment({
        metrics,
        ips_targets: ipsTargets,
        ips_profile: ipsProfile
      }).then(data => {
        setAlignment(data)
        setLoading(false)
      }).catch(() => {
        setLoading(false)
      })
    }
  }, [metrics, ipsTargets, ipsProfile])

  if (!metrics || !ipsTargets) return null

  const getAlignmentStatus = () => {
    if (!alignment?.is_aligned) return { isAligned: false, text: '⚠ Needs Adjustment' }
    return {
      isAligned: alignment.is_aligned,
      text: alignment.is_aligned ? '✓ Fully Aligned' : '⚠ Needs Adjustment'
    }
  }

  const cleanBulletText = (bullet: string) => {
    return bullet
      .replace(/^📊\s*/, '')
      .replace(/^✅\s*/, '')
      .replace(/^⚠️\s*/, '')
      .replace(/^⚠\s*/, '')
      .replace(/^\[WARN]\s*/, '')
      .replace(/^\[WARN]/, '')
      .replace(/^🎉\s*/, '')
      .replace(/\*\*/g, '')
  }

  const getBulletStyle = (bullet: string) => {
    if (bullet.startsWith('✅') || bullet.startsWith('🎉')) {
      return {
        background: '#f0fdf4',
        borderLeft: '4px solid #1a6e4a',
        color: '#166534'
      }
    } else if (bullet.startsWith('⚠️') || bullet.startsWith('⚠') || bullet.startsWith('[WARN]')) {
      return {
        background: '#fffbeb',
        borderLeft: '4px solid #c9943a',
        color: '#3a4150'
      }
    } else if (bullet.startsWith('📊')) {
      return {
        background: '#f0f4ff',
        borderLeft: '4px solid #2556a0',
        color: '#1a3d6e',
        fontWeight: '600'
      }
    } else {
      return {
        background: '#f8fafc',
        borderLeft: '4px solid #64748b',
        color: '#3a4150'
      }
    }
  }

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
        <div className="flex items-center justify-between">
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
              <span style={{ fontSize: '20px' }}>🎯</span>
            </div>
            <div>
              <div style={{
                fontFamily: 'DM Serif Display, Georgia, serif',
                fontSize: '19px',
                fontWeight: '700',
                color: '#0d1117',
                letterSpacing: '-0.3px'
              }}>
                IPS Alignment
              </div>
              <div style={{
                fontFamily: 'Arial',
                fontSize: '14px',
                color: '#94a3b8',
                marginTop: '3px'
              }}>
                How your portfolio matches your Investment Policy Statement
              </div>
            </div>
          </div>
          {!loading && alignment && (
            <span style={{
              ...getAlignmentStatus().isAligned ? {
                background: '#dcfce7',
                color: '#166534'
              } : {
                background: '#fee2e2',
                color: '#991b1b'
              },
              padding: '5px 14px',
              borderRadius: '20px',
              fontSize: '13px',
              fontWeight: '700',
              fontFamily: 'Arial, sans-serif'
            }}>
              {getAlignmentStatus().text}
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{
          textAlign: 'center',
          padding: '32px 0',
          color: '#94a3b8',
          fontFamily: 'Arial',
          fontSize: '15px'
        }}>
          Checking alignment...
        </div>
      ) : alignment ? (
        <div>
          {alignment.bullets.map((bullet: string, i: number) => {
            const cleanText = cleanBulletText(bullet)
            const bulletStyle = getBulletStyle(bullet)
            
            return (
              <div key={i} style={{
                padding: '16px 20px',
                marginBottom: '10px',
                borderRadius: '10px',
                fontSize: '15px',
                lineHeight: '1.75',
                fontFamily: 'Arial, sans-serif',
                display: 'block',
                width: '100%',
                ...bulletStyle
              }}>
                {cleanText}
              </div>
            )
          })}
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '32px 0',
          color: '#94a3b8',
          fontFamily: 'Arial',
          fontSize: '15px'
        }}>
          Unable to check alignment
        </div>
      )}
    </div>
  )
}

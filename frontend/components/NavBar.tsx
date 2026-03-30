'use client'
import { useAppStore } from '@/store/useAppStore'
import { useRouter, usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'

export default function NavBar() {
  const { currency, setCurrency, ipsProfile, resetIPS } =
    useAppStore()
  const router = useRouter()
  const pathname = usePathname()
  
  // Check if we're on the analyze page
  const isAnalyzePage = pathname === '/analyze'
  
  // Arrow animation state
  const [showArrow, setShowArrow] = useState(false)
  const [hasSeenArrow, setHasSeenArrow] = useState(false)
  
  // Show arrow when entering analyze page for the first time
  useEffect(() => {
    if (isAnalyzePage && !hasSeenArrow) {
      setShowArrow(true)
      setHasSeenArrow(true)
      // Hide callout after 3 seconds
      const timer = setTimeout(() => {
        setShowArrow(false)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [isAnalyzePage, hasSeenArrow])

  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = `
      @keyframes fadeInOut {
        0% {
          opacity: 0;
          transform: translateY(-10px);
        }
        10% {
          opacity: 1;
          transform: translateY(0);
        }
        90% {
          opacity: 1;
          transform: translateY(0);
        }
        100% {
          opacity: 0;
          transform: translateY(-10px);
        }
      }
    `
    document.head.appendChild(style)
    return () => {
      document.head.removeChild(style)
    }
  }, [])

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      background: 'rgba(255,255,255,0.92)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid #e2e8f0',
    }}>
      <div style={{
        maxWidth: 1200,
        margin: '0 auto',
        padding: '0 32px',
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>

        {/* Logo */}
        <div
          onClick={() => { resetIPS(); router.push('/') }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            cursor: 'pointer',
            textDecoration: 'none',
          }}
        >
          <div style={{
            width: 34,
            height: 34,
            borderRadius: 9,
            background: '#1a3d6e',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            fontSize: 16,
            fontWeight: 800,
            fontFamily: 'Georgia, serif',
            flexShrink: 0,
          }}>
            P
          </div>
          <span style={{
            fontFamily: "'DM Serif Display', Georgia, serif",
            fontSize: 22,
            color: '#0d1117',
            letterSpacing: '-0.5px',
            lineHeight: 1,
          }}>
            ortfolio
            <span style={{ color: '#2556a0' }}>IQ</span>
          </span>
        </div>

        {/* Right side */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}>
          {ipsProfile && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 7,
              background: '#dbeafe',
              border: '1px solid #2556a0',
              borderRadius: 20,
              padding: '5px 14px',
              fontSize: 12,
              fontWeight: 600,
              color: '#1a3d6e',
              fontFamily: 'Arial, sans-serif',
            }}>
              <span style={{
                width: 7,
                height: 7,
                borderRadius: '50%',
                background: '#4ade80',
                display: 'inline-block',
                flexShrink: 0,
              }} />
              IPS: {ipsProfile}
            </div>
          )}
          {isAnalyzePage && (
            <div style={{ position: 'relative' }}>
              {showArrow && (
                <div style={{
                  position: 'absolute',
                  top: '45px',
                  right: '0',
                  zIndex: -1,
                  animation: 'fadeInOut 3s ease-in-out'
                }}>
                  <div style={{
                    background: '#2556a0',
                    color: 'white',
                    padding: '8px 14px',
                    borderRadius: '8px',
                    fontSize: '13px',
                    fontWeight: '600',
                    fontFamily: 'Arial, sans-serif',
                    whiteSpace: 'nowrap',
                    boxShadow: '0 4px 16px rgba(37, 86, 160, 0.3)',
                    border: '2px solid #ffffff',
                    position: 'relative'
                  }}>
                    💰 Select currency for analysis
                    <div style={{
                      position: 'absolute',
                      top: '-6px',
                      right: '20px',
                      width: '12px',
                      height: '12px',
                      background: '#2556a0',
                      transform: 'rotate(45deg)',
                      borderLeft: '2px solid #ffffff',
                      borderTop: '2px solid #ffffff'
                    }}></div>
                  </div>
                </div>
              )}
              <select
                value={currency}
                onChange={e => setCurrency(e.target.value)}
                title="Select currency for portfolio analysis and reporting"
                style={{
                  fontSize: 13,
                  fontWeight: 500,
                  border: '1px solid #e2e8f0',
                  borderRadius: 8,
                  padding: '7px 28px 7px 12px',
                  background: '#ffffff',
                  color: '#0d1117',
                  cursor: 'pointer',
                  outline: 'none',
                  fontFamily: 'Arial, sans-serif',
                  appearance: 'none',
                  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%237a8394' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E")`,
                  backgroundRepeat: 'no-repeat',
                  backgroundPosition: 'right 10px center',
                }}
              >
                <option value="CAD">🇨🇦 CAD</option>
                <option value="USD">🇺🇸 USD</option>
                <option value="GBP">🇬🇧 GBP</option>
                <option value="EUR">🇪🇺 EUR</option>
              </select>
            </div>
          )}
        </div>

      </div>
    </header>
  )
}

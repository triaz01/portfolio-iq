'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/lib/useAppStore'
import PortfolioInput from '@/components/dashboard/PortfolioInput'
import StatGrid from '@/components/dashboard/StatGrid'
import GrowthChart from '@/components/dashboard/GrowthChart'
import Projections from '@/components/dashboard/Projections'
import CorrelationMatrix from '@/components/dashboard/CorrelationMatrix'
import TradingSignals from '@/components/dashboard/TradingSignals'
import IPSAlignment from '@/components/dashboard/IPSAlignment'
import MonteCarlo from '@/components/dashboard/MonteCarlo'
import PDFBar from '@/components/dashboard/PDFBar'

export default function AnalyzePage() {
  const router = useRouter()
  const { ipsProfile, ipsTargets, metrics } = useAppStore()

  const getIPSBestPracticeText = (profile: string) => {
    const normalized = profile.toLowerCase()

    if (normalized.includes('conservative')) {
      return 'This profile focuses on protecting your capital and keeping results steadier over time. It typically uses more high-quality fixed income and less equity risk.'
    }

    if (normalized.includes('moderate')) {
      return 'This profile aims for a balance between growth and stability. It combines equities and fixed income so your portfolio can grow while keeping risk at a comfortable level.'
    }

    if (normalized.includes('aggressive')) {
      return 'This profile is designed for higher long-term growth and accepts larger short-term swings. It usually keeps a higher equity allocation and broad diversification.'
    }

    return 'This profile sets a clear direction for return goals, risk level, and diversification so investment decisions stay consistent with your objectives.'
  }

  const getTargetRangesText = () => {
    if (!ipsTargets) return ''

    const targets = ipsTargets as {
      beta_range?: [number, number]
      volatility_range?: [number, number]
      yield_min?: number
      yield_max?: number
    }

    const [betaMin, betaMax] = targets.beta_range || [0, 0]
    const [volMin, volMax] = targets.volatility_range || [0, 0]
    const yieldMin = targets.yield_min ?? 0
    const yieldMax = targets.yield_max ?? 1

    return `Target ranges: Beta ${betaMin.toFixed(2)}-${betaMax.toFixed(2)} | Volatility ${(volMin * 100).toFixed(0)}%-${(volMax * 100).toFixed(0)}% | Dividend Yield ${(yieldMin * 100).toFixed(0)}%-${(yieldMax * 100).toFixed(0)}%`
  }

  useEffect(() => {
    if (!ipsProfile || !ipsTargets) {
      router.replace('/')
    }
  }, [ipsProfile, ipsTargets, router])

  if (!ipsProfile) return null

  return (
    <div style={{ 
      padding: '36px 36px 140px 36px',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      <div 
        style={{
          background: '#dbeafe',
          border: '1px solid #2556a0',
          borderRadius: '14px',
          padding: '16px 28px',
          marginBottom: '28px'
        }}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2.5"
              style={{
                fontFamily: 'Arial',
                fontSize: '16px'
              }}>
              <span 
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#4ade80',
                  display: 'inline-block'
                }} />
              <span style={{ color: '#1e3a8a', fontWeight: 'bold' }}>
                Active IPS Profile:
              </span>
              <span style={{ color: '#1e3a8a', fontWeight: '900' }}>
                {ipsProfile}
              </span>
            </div>
            <p
              style={{
                marginTop: '8px',
                marginBottom: 0,
                color: '#475569',
                fontFamily: 'Arial, sans-serif',
                fontSize: '14px',
                lineHeight: '1.6',
                maxWidth: '840px'
              }}
            >
              {getIPSBestPracticeText(ipsProfile)}
            </p>
            <p
              style={{
                marginTop: '6px',
                marginBottom: 0,
                color: '#1e3a8a',
                fontFamily: 'Arial, sans-serif',
                fontSize: '13px',
                fontWeight: '700',
                lineHeight: '1.5'
              }}
            >
              {getTargetRangesText()}
            </p>
          </div>
          <button
            onClick={() => {
              useAppStore.getState().resetIPS()
              router.push('/')
            }}
            style={{
              fontFamily: 'Arial',
              fontSize: '15px',
              color: '#1e3a8a',
              border: '1px solid #1e3a8a',
              borderRadius: '8px',
              padding: '6px 12px',
              background: 'transparent',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = '#dbeafe'
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'transparent'
            }}>
            ↺ Reset IPS
          </button>
        </div>
      </div>

      <PortfolioInput />

      {metrics && (
        <>
          <StatGrid />
          <GrowthChart />
          <Projections />
          <CorrelationMatrix />
          <TradingSignals />
          <IPSAlignment />
          <MonteCarlo />
        </>
      )}

      <PDFBar />
    </div>
  )
}

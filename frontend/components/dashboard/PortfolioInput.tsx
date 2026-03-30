'use client'
import { useState } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { analyzePortfolio, getSignals } from '@/lib/api'

export default function PortfolioInput() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressStage, setProgressStage] = useState('')
  const { currency, setMetrics, setSignals } = useAppStore()

  async function handleAnalyze() {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    setSuccess(false)
    setProgress(0)
    setProgressStage('Initializing analysis...')
    
    try {
      // Stage 1: Portfolio Analysis (30%)
      setProgress(10)
      setProgressStage('Fetching market data...')
      const data = await analyzePortfolio({ text, currency })
      
      setProgress(30)
      setProgressStage('Processing portfolio metrics...')
      
      // Store all portfolio analysis data in the app store
      useAppStore.setState({
        metrics: data.metrics,
        chartData: data.chart_data,
        projectionDf: data.projection_df,
        correlationMatrix: data.correlation_matrix
      })
      
      // Stage 2: Trading Signals (50%)
      const tickers = Object.keys(
        data.metrics?.weights || {}
      )
      if (tickers.length > 0) {
        setProgress(50)
        setProgressStage('Analyzing trading signals...')
        const sigData = await getSignals(tickers)
        setSignals(sigData.signals)
        setProgress(80)
        setProgressStage('Finalizing analysis...')
      } else {
        setProgress(80)
        setProgressStage('Finalizing analysis...')
      }
      
      // Stage 3: Complete (100%)
      setProgress(100)
      setProgressStage('Analysis complete!')
      setSuccess(true)
      
      // Reset progress after a short delay
      setTimeout(() => {
        setProgress(0)
        setProgressStage('')
      }, 1500)
      
    } catch (e: any) {
      setProgress(0)
      setProgressStage('')
      setError(e?.response?.data?.detail || 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }

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
        <div style={{
          background: 'linear-gradient(135deg, #1a3d6e, #2556a0)',
          padding: '28px 44px',
          margin: '-28px -28px 20px -28px',
          borderRadius: '20px 20px 0 0'
        }}>
          <div style={{
            fontSize: 12, fontWeight: 700,
            letterSpacing: '1.6px',
            textTransform: 'uppercase' as const,
            color: 'rgba(255,255,255,0.6)',
            marginBottom: 6,
            fontFamily: 'Arial, sans-serif',
          }}>
            Step 2 of 3
          </div>
          <div style={{
            fontFamily: "'DM Serif Display', Georgia, serif",
            fontSize: 30, fontWeight: 700,
            color: '#ffffff', letterSpacing: '-0.5px',
            lineHeight: 1.15,
          }}>
            Enter and Analyze Portfolio Holdings
          </div>
          <div style={{
            fontSize: 15, color: 'rgba(255,255,255,0.65)',
            fontFamily: 'Arial, sans-serif',
            marginTop: 4,
            lineHeight: 1.4,
          }}>
            Paste tickers and share counts and press Analyze Portfolio button
          </div>
        </div>
      </div>

      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder={"AAPL 100\nMSFT 50\nRY.TO 75"}
        style={{
          width: '100%',
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          background: '#f8fafc',
          padding: '14px 16px',
          fontSize: '16px',
          fontFamily: 'monospace',
          color: '#0d1117',
          resize: 'none',
          outline: 'none',
          lineHeight: '1.8',
          minHeight: '120px',
          marginBottom: '16px',
          transition: 'all 0.2s'
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = '#2556a0'
          e.currentTarget.style.background = '#ffffff'
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = '#e2e8f0'
          e.currentTarget.style.background = '#f8fafc'
        }} />

      {loading && progress > 0 && (
        <div style={{
          marginTop: '16px',
          padding: '16px',
          background: '#f8fafc',
          borderRadius: '12px',
          border: '1px solid #e2e8f0'
        }}>
          <div style={{
            fontSize: '13px',
            color: '#64748b',
            fontFamily: 'Arial, sans-serif',
            marginBottom: '8px',
            fontWeight: '500'
          }}>
            {progressStage}
          </div>
          <div style={{
            width: '100%',
            height: '8px',
            backgroundColor: '#e2e8f0',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${progress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #1a3d6e, #2556a0)',
              borderRadius: '4px',
              transition: 'width 0.3s ease',
              position: 'relative'
            }}>
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)'
              }}></div>
            </div>
          </div>
          <div style={{
            fontSize: '11px',
            color: '#94a3b8',
            fontFamily: 'Arial, sans-serif',
            marginTop: '6px',
            textAlign: 'right'
          }}>
            {progress}% complete
          </div>
        </div>
      )}

      <button
        onClick={handleAnalyze}
        disabled={loading || !text.trim()}
        style={{
          width: '100%',
          padding: '16px 24px',
          borderRadius: '12px',
          fontSize: '17px',
          fontWeight: '700',
          color: '#ffffff',
          background:'linear-gradient(135deg,#1a3d6e,#2556a0)',
          boxShadow:'0 4px 14px rgba(26,61,110,0.25)',
          border: 'none',
          cursor: loading || !text.trim() ? 'not-allowed' : 'pointer',
          opacity: loading || !text.trim() ? '0.5' : '1',
          transition: 'all 0.2s'
        }}>
        {loading ? 'Analyzing...' : 'Analyze Portfolio'}
      </button>

      {error && (
        <div style={{ marginTop: '20px' }} className="p-3 rounded-xl bg-red-50 
          border border-red-200 text-red-700"
          >
          {error}
        </div>
      )}
      {success && (
        <div style={{ marginTop: '20px' }} className="p-3 rounded-xl bg-green-50 
          border border-green-200 text-green-700 font-medium"
          >
          ✅ Analysis complete — results displayed below
        </div>
      )}
    </div>
  )
}

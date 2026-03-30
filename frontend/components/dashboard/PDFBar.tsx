'use client'
import { useState, useEffect, useRef } from 'react'
import { useAppStore } from '@/store/useAppStore'
import { generatePDF, runMonteCarlo, checkAlignment } from '@/lib/api'

export default function PDFBar() {
  const { metrics, ipsProfile, ipsTargets, projectionDf, correlationMatrix, chartData, signals, currency } = useAppStore()
  const [loading, setLoading] = useState(false)
  const [shouldPulse, setShouldPulse] = useState(false)
  const prevMetricsRef = useRef<any>(null)
  // Use same default as MonteCarlo component
  const [years] = useState(20)
  const [withdrawal] = useState(0)

  // Trigger pulse animation when metrics first becomes available
  useEffect(() => {
    if (metrics && !prevMetricsRef.current) {
      setShouldPulse(true)
      const timer = setTimeout(() => setShouldPulse(false), 600)
      return () => clearTimeout(timer)
    }
    prevMetricsRef.current = metrics
  }, [metrics])

  async function handleDownloadPDF() {
    if (!metrics || !ipsProfile || !ipsTargets || !projectionDf) return

    setLoading(true)
    try {
      // Get alignment data the same way as IPSAlignment component
      const alignmentResponse = await checkAlignment({
        metrics,
        ips_targets: ipsTargets,
        ips_profile: ipsProfile
      })

      // Generate Monte Carlo data using same parameters as MonteCarlo component
      const mcResponse = await runMonteCarlo({
        initial_value: (metrics as any).total_value,
        cagr: (metrics as any).annualized_return,
        volatility: (metrics as any).annual_volatility,
        years,
        simulations: 500,
        annual_withdrawal: withdrawal
      })

      const pdfBlob = await generatePDF({
        metrics,
        ips_profile: ipsProfile,
        ips_alignment_bullets: alignmentResponse?.bullets || [],
        ips_targets: ipsTargets,
        projection_df_json: projectionDf,
        correlation_matrix: correlationMatrix,
        chart_data: chartData,
        signals: signals || [],
        monte_carlo_data: mcResponse.data, // Pass the exact Monte Carlo data
        currency: currency || 'CAD'
      })

      // Create download link
      const url = window.URL.createObjectURL(pdfBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'portfolio-analysis.pdf'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('PDF generation failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const isActive = !!metrics

  return (
    <>
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.04); }
        }
        .pulse-once {
          animation: pulse 0.6s ease-out;
        }
      `}</style>
      
      <div 
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          zIndex: 50,
          background: isActive 
            ? 'linear-gradient(135deg, #1a3d6e, #2556a0)'
            : 'linear-gradient(135deg, #94a3b8, #64748b)',
          borderRadius: '16px 16px 0 0',
          transition: 'all 0.4s ease'
        }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '20px 32px 32px 32px',
        }}>
          <div style={{
            background: isActive 
              ? 'linear-gradient(135deg, #1a3d6e, #2556a0)'
              : 'linear-gradient(135deg, #94a3b8, #64748b)',
            padding: '28px 44px',
            margin: '-20px -32px 20px -32px',
            borderRadius: '16px 16px 0 0'
          }}>
            <div style={{
              fontSize: 12, fontWeight: 700,
              letterSpacing: '1.6px',
              textTransform: 'uppercase' as const,
              color: 'rgba(255,255,255,0.6)',
              marginBottom: 6,
              fontFamily: 'Arial, sans-serif',
            }}>
              Step 3 of 3
            </div>
            <div style={{
              fontFamily: "'DM Serif Display', Georgia, serif",
              fontSize: 30, fontWeight: 700,
              color: '#ffffff', letterSpacing: '-0.5px',
              lineHeight: 1.15,
            }}>
              Download the Report
            </div>
            <div style={{
              fontSize: 15, color: 'rgba(255,255,255,0.65)',
              fontFamily: 'Arial, sans-serif',
              marginTop: 4,
              lineHeight: 1.4,
            }}>
              {isActive
                ? 'Export an institutional-grade PDF tear sheet with all analysis and IPS alignment.'
                : 'Enter your holdings above and click Analyze Portfolio to get started'}
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div></div>
            
            <button
            onClick={handleDownloadPDF}
            disabled={!isActive || loading}
            className={shouldPulse ? 'pulse-once' : ''}
            style={{
              padding: '13px 28px',
              borderRadius: '10px',
              fontSize: '15px',
              fontWeight: '700',
              fontFamily: 'Arial, sans-serif',
              transition: 'all 0.2s',
              whiteSpace: 'nowrap',
              flexShrink: 0,
              background: loading 
                ? '#94a3b8'
                : isActive 
                  ? '#c9943a'
                  : 'rgba(255,255,255,0.15)',
              color: isActive || loading ? '#ffffff' : 'rgba(255,255,255,0.4)',
              cursor: isActive && !loading ? 'pointer' : 'not-allowed',
              boxShadow: isActive && !loading 
                ? '0 4px 14px rgba(201,148,58,0.35)'
                : 'none',
              border: isActive || loading ? 'none' : '1px solid rgba(255,255,255,0.2)'
            }}>
            {loading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTop: '2px solid #ffffff',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                <span>Generating Report...</span>
              </div>
            ) : '⬇ Generate PDF Report'}
            </button>
            
            {loading && (
              <div style={{
                marginTop: '16px',
                padding: '12px 16px',
                background: 'rgba(255,255,255,0.1)',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.2)'
              }}>
                <div style={{
                  fontSize: '12px',
                  color: 'rgba(255,255,255,0.8)',
                  fontFamily: 'Arial, sans-serif',
                  textAlign: 'center'
                }}>
                  <div style={{ marginBottom: '8px' }}>Creating your portfolio analysis report...</div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    justifyContent: 'center'
                  }}>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      backgroundColor: '#ffffff',
                      borderRadius: '50%',
                      animation: 'pulse 1.4s ease-in-out infinite'
                    }}></div>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      backgroundColor: '#ffffff',
                      borderRadius: '50%',
                      animation: 'pulse 1.4s ease-in-out infinite 0.2s'
                    }}></div>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      backgroundColor: '#ffffff',
                      borderRadius: '50%',
                      animation: 'pulse 1.4s ease-in-out infinite 0.4s'
                    }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 80%, 100% { 
            transform: scale(0.8);
            opacity: 0.5;
          }
          40% { 
            transform: scale(1);
            opacity: 1;
          }
        }
        .pulse-once {
          animation: pulse 0.6s ease-out;
        }
      `}</style>
    </>
  )
}

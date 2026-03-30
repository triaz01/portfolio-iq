'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAppStore } from '@/store/useAppStore'
import { generateIPS } from '@/lib/api'

function SectionHeader({
  icon, iconBg, title, sub,
}: {
  icon: string; iconBg: string
  title: string; sub: string
}) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center',
      gap: 14, marginBottom: 20,
    }}>
      <div style={{
        width: 42, height: 42, borderRadius: 11,
        background: iconBg, display: 'flex',
        alignItems: 'center', justifyContent: 'center',
        fontSize: 20, flexShrink: 0,
      }}>
        {icon}
      </div>
      <div>
        <div style={{
          fontSize: 17, fontWeight: 700,
          color: '#0d1117',
          fontFamily: "'DM Serif Display', Georgia, serif",
        }}>
          {title}
        </div>
        <div style={{
          fontSize: 14, color: '#94a3b8',
          fontFamily: 'Arial, sans-serif',
          marginTop: 2,
        }}>
          {sub}
        </div>
      </div>
    </div>
  )
}

function Chip({
  label, active, onClick,
}: {
  label: string; active: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '10px 20px',
        borderRadius: 10,
        border: active
          ? '2px solid #2556a0'
          : '1.5px solid #e2e8f0',
        background: active ? '#dbeafe' : '#f8fafc',
        color: active ? '#1a3d6e' : '#475569',
        fontSize: 15, fontWeight: active ? 600 : 500,
        cursor: 'pointer',
        fontFamily: 'Arial, sans-serif',
        transition: 'all 0.15s ease',
        outline: 'none',
        lineHeight: 1.4,
      }}
    >
      {label}
    </button>
  )
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      fontSize: 15, fontWeight: 600,
      color: '#3a4150', marginBottom: 12,
      fontFamily: 'Arial, sans-serif',
    }}>
      {children}
    </div>
  )
}

function Divider() {
  return <div style={{
    height: 1, background: '#f1f5f9',
    margin: '32px 0',
  }} />
}

export default function IPSForm() {
  const router = useRouter()
  const setIPS = useAppStore(s => s.setIPS)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    time_horizon: 10,
    liquidity: 'Low (< 10%)',
    objective: 'Capital Preservation',
    crash_reaction: 'Do nothing and wait',
    knowledge: 'Intermediate',
  })
  const set = (k: string, v: any) =>
    setForm(f => ({ ...f, [k]: v }))

  async function handleSubmit() {
    setLoading(true); setError('')
    try {
      const res = await generateIPS(form)
      setIPS(res.profile, res.targets)
      router.push('/analyze')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 
        'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      background: '#ffffff',
      border: '1px solid #e2e8f0',
      borderRadius: 20,
      overflow: 'hidden',
      boxShadow: '0 2px 20px rgba(13,17,23,0.06)',
      marginBottom: 24,
    }}>

      {/* Card Header Bar */}
      <div style={{
        background: 'linear-gradient(135deg, #1a3d6e, #2556a0)',
        padding: '28px 44px',
      }}>
        <div style={{
          fontSize: 12, fontWeight: 700,
          letterSpacing: '1.6px',
          textTransform: 'uppercase' as const,
          color: 'rgba(255,255,255,0.6)',
          marginBottom: 6,
          fontFamily: 'Arial, sans-serif',
        }}>
          Step 1 of 3
        </div>
        <div style={{
          fontFamily:
            "'DM Serif Display', Georgia, serif",
          fontSize: 30, fontWeight: 700,
          color: '#ffffff', letterSpacing: '-0.5px',
          lineHeight: 1.15,
        }}>
          Define Your Investment Policy
        </div>
        <div style={{
          fontSize: 15, color: 'rgba(255,255,255,0.65)',
          lineHeight: 1.65, marginTop: 8,
          fontFamily: 'Arial, sans-serif',
          maxWidth: 560,
        }}>
          Answer a few questions to create your 
          personalized IPS. This guides every metric 
          and alignment check in the analysis.
        </div>
      </div>

      {/* Form Body */}
      <div style={{ padding: '40px 44px' }}>

        {/* TIME HORIZON */}
        <SectionHeader
          icon="⏱" iconBg="#dbeafe"
          title="Time Horizon & Liquidity"
          sub="When will you need to access this capital?"
        />
        <Label>
          Investment horizon:{' '}
          <span style={{ color: '#2556a0', fontWeight: 700 }}>
            {form.time_horizon} Years
          </span>
        </Label>
        <input
          type="range" min={1} max={30}
          value={form.time_horizon}
          onChange={e =>
            set('time_horizon', Number(e.target.value))
          }
          style={{ width: '100%', marginBottom: 24, display: 'block' }}
        />
        <Label>Cash needs within 12 months</Label>
        <div style={{
          display: 'flex', flexWrap: 'wrap' as const,
          gap: 8,
        }}>
          {['None (0%)', 'Low (< 10%)',
            'Moderate (10-25%)', 'High (> 25%)']
            .map(o => (
              <Chip key={o} label={o}
                active={form.liquidity === o}
                onClick={() => set('liquidity', o)} />
            ))}
        </div>

        <Divider />

        {/* OBJECTIVES */}
        <SectionHeader
          icon="🎯" iconBg="#fef3c7"
          title="Investment Objectives"
          sub="What is the primary goal for this portfolio?"
        />
        <div style={{
          display: 'flex', flexWrap: 'wrap' as const,
          gap: 8,
        }}>
          {['Capital Preservation', 'Steady Income',
            'Balanced Growth',
            'Maximum Capital Appreciation']
            .map(o => (
              <Chip key={o} label={o}
                active={form.objective === o}
                onClick={() => set('objective', o)} />
            ))}
        </div>

        <Divider />

        {/* RISK */}
        <SectionHeader
          icon="📉" iconBg="#fce7f3"
          title="Risk Tolerance"
          sub="How do you respond to market volatility?"
        />
        <Label>
          If your portfolio dropped 20% in one month,
          what would you do?
        </Label>
        <div style={{
          display: 'flex', flexWrap: 'wrap' as const,
          gap: 8, marginBottom: 24,
        }}>
          {['Sell to avoid further losses',
            'Do nothing and wait',
            'Buy more at a discount']
            .map(o => (
              <Chip key={o} label={o}
                active={form.crash_reaction === o}
                onClick={() =>
                  set('crash_reaction', o)} />
            ))}
        </div>
        <Label>
          Investment experience:{' '}
          <span style={{ color: '#2556a0', fontWeight: 700 }}>
            {form.knowledge}
          </span>
        </Label>
        <div style={{
          display: 'flex', flexWrap: 'wrap' as const,
          gap: 8,
        }}>
          {['Novice', 'Intermediate',
            'Advanced', 'Expert']
            .map(o => (
              <Chip key={o} label={o}
                active={form.knowledge === o}
                onClick={() =>
                  set('knowledge', o)} />
            ))}
        </div>

        <Divider />

        {error && (
          <div style={{
            padding: '12px 16px', borderRadius: 10,
            background: '#fee2e2',
            border: '1px solid #fca5a5',
            color: '#991b1b', fontSize: 15,
            marginBottom: 16,
            fontFamily: 'Arial, sans-serif',
          }}>
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: '100%',
            padding: '18px 24px',
            borderRadius: 12,
            border: 'none',
            background: loading
              ? '#94a3b8'
              : 'linear-gradient(135deg,#1a3d6e,#2556a0)',
            color: '#ffffff',
            fontSize: 17,
            fontWeight: 700,
            cursor: loading
              ? 'not-allowed' : 'pointer',
            fontFamily: 'Arial, sans-serif',
            boxShadow: loading ? 'none'
              : '0 4px 20px rgba(26,61,110,0.3)',
            transition: 'all 0.2s',
            letterSpacing: '0.3px',
          }}
        >
          {loading
            ? 'Generating your IPS...'
            : 'Generate My IPS & Analyze Portfolio →'}
        </button>

      </div>
    </div>
  )
}

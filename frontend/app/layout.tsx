import type { Metadata } from 'next'
import './globals.css'
import NavBar from '@/components/NavBar'
import Providers from '@/components/Providers'

export const metadata: Metadata = {
  title: 'PortfolioIQ — Institutional Portfolio Analysis',
  description: 'Generate IPS, analyze risk, run Monte Carlo simulations, and export PDF reports for any client portfolio.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ background: '#f8fafc' }}>
        <Providers>
          <NavBar />
          <main style={{
            maxWidth: 1200,
            margin: '0 auto',
            padding: '32px 32px 80px 32px',
          }}>
            {children}
          </main>
        </Providers>
      </body>
    </html>
  )
}

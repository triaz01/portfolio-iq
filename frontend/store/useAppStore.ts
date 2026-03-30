import { create } from 'zustand'

interface AppStore {
  ipsProfile: string | null
  ipsTargets: object | null
  metrics: object | null
  projectionDf: object[] | null
  correlationMatrix: object | null
  chartData: object | null
  signals: object[] | null
  summary: string | null
  currency: string
  mcYears: number
  mcWithdrawal: number
  setIPS: (profile: string, targets: object) => void
  setMetrics: (data: any) => void
  setSignals: (signals: object[]) => void
  setCurrency: (c: string) => void
  setMCParams: (years: number, withdrawal: number) => void
  resetIPS: () => void
}

export const useAppStore = create<AppStore>((set) => ({
  ipsProfile: null,
  ipsTargets: null,
  metrics: null,
  projectionDf: null,
  correlationMatrix: null,
  chartData: null,
  signals: null,
  summary: null,
  currency: 'CAD',
  mcYears: 20,
  mcWithdrawal: 0,
  setIPS: (profile, targets) =>
    set({ ipsProfile: profile, ipsTargets: targets }),
  setMetrics: (data: any) => set({
    metrics: data.metrics,
    projectionDf: data.projection_df,
    correlationMatrix: data.correlation_matrix,
    chartData: data.chart_data,
    summary: data.summary,
  }),
  setSignals: (signals) => set({ signals }),
  setCurrency: (currency) => set({ currency }),
  setMCParams: (years, withdrawal) => set({ mcYears: years, mcWithdrawal: withdrawal }),
  resetIPS: () => set({
    ipsProfile: null,
    ipsTargets: null,
    metrics: null,
    projectionDf: null,
    correlationMatrix: null,
    chartData: null,
    signals: null,
    summary: null,
  }),
}))

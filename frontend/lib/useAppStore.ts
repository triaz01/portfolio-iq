import { create } from 'zustand'

interface AppStore {
  ipsProfile: string | null
  ipsTargets: object | null
  metrics: object | null
  projectionDf: object[] | null
  correlationMatrix: object | null
  chartData: object | null
  signals: object[] | null
  currency: string
  setIPS: (profile: string, targets: object) => void
  setMetrics: (data: object) => void
  setSignals: (signals: object[]) => void
  setCurrency: (c: string) => void
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
  currency: 'CAD',
  setIPS: (profile, targets) =>
    set({ ipsProfile: profile, ipsTargets: targets }),
  setMetrics: (data: any) => set({
    metrics: data.metrics,
    projectionDf: data.projection_df,
    correlationMatrix: data.correlation_matrix,
    chartData: data.chart_data,
  }),
  setSignals: (signals) => set({ signals }),
  setCurrency: (currency) => set({ currency }),
  resetIPS: () => set({
    ipsProfile: null, ipsTargets: null,
    metrics: null, projectionDf: null,
    correlationMatrix: null, chartData: null,
    signals: null,
  }),
}))

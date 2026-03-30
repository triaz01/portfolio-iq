import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const generateIPS = (data: object) =>
  api.post('/ips', data).then(r => r.data)

export const analyzePortfolio = (data: object) =>
  api.post('/analyze', data).then(r => r.data)

export const getSignals = (tickers: string[]) =>
  api.post('/signals', { tickers }).then(r => r.data)

export const checkAlignment = (data: object) =>
  api.post('/alignment', data).then(r => r.data)

export const runMonteCarlo = (data: object) =>
  api.post('/montecarlo', data).then(r => r.data)

export const generatePDF = (data: object) =>
  api.post('/pdf', data, { responseType: 'blob' })
    .then(r => r.data)

export default api

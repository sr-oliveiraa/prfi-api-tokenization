import axios from 'axios'

// Configurar base URL da API
const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8080/api'
  : '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Types
export interface DashboardStats {
  totalRequests: number
  successRate: number
  avgResponseTime: number
  tokensEarned: number
  activeAPIs: number
  failedRequests: number
}

export interface Activity {
  id: number
  type: string
  status: 'success' | 'error' | 'warning' | 'info'
  message: string
  timestamp: number
}

export interface APIStatus {
  name: string
  url: string
  status: 'online' | 'offline' | 'warning'
  response_time: number
  success_rate: number
  last_check: number
}

export interface BlockchainInfo {
  network: string
  contract_address?: string
  connected: boolean
  latest_block: number
  gas_price: string
  tokens_balance: number
}

export interface ChartData {
  timestamp: string
  requests: number
  success_rate: number
  response_time: number
}

// API Functions
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/dashboard/stats')
  return response.data
}

export const getRecentActivity = async (): Promise<Activity[]> => {
  const response = await api.get('/dashboard/activity')
  return response.data
}

export const getAPIStatus = async (): Promise<APIStatus[]> => {
  const response = await api.get('/apis/status')
  return response.data
}

export const getBlockchainInfo = async (): Promise<BlockchainInfo> => {
  const response = await api.get('/blockchain/info')
  return response.data
}

export const getPerformanceChart = async (): Promise<ChartData[]> => {
  const response = await api.get('/performance/chart')
  return response.data
}

export const testAPI = async (apiData: {
  url: string
  method: string
}): Promise<{
  success: boolean
  status_code: number
  response_time: number
  error?: string
}> => {
  const response = await api.post('/test/api', apiData)
  return response.data
}

export const deployContract = async (deployData: {
  network: string
}): Promise<{
  success: boolean
  contract_address: string
  transaction_hash: string
  network: string
  gas_used: number
}> => {
  const response = await api.post('/deploy/contract', deployData)
  return response.data
}

export const getSystemStatus = async (): Promise<{
  status: string
  version: string
  timestamp: number
  config: {
    project_name: string
    network: string
    apis_count: number
    monitoring_enabled: boolean
  }
}> => {
  const response = await api.get('/status')
  return response.data
}

export default api

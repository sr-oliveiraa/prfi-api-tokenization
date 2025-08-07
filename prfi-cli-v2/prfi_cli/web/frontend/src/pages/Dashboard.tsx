import React from 'react'
import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import {
  Activity,
  TrendingUp,
  Zap,
  Globe,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
} from 'lucide-react'

// Components
import StatsCard from '../components/StatsCard'
import Chart from '../components/Chart'
import RecentActivity from '../components/RecentActivity'
import APIStatus from '../components/APIStatus'
import TokenBalance from '../components/TokenBalance'

// Services
import { getDashboardStats, getRecentActivity, getAPIStatus } from '../services/api'

// Types
interface DashboardStats {
  totalRequests: number
  successRate: number
  avgResponseTime: number
  tokensEarned: number
  activeAPIs: number
  failedRequests: number
}

const Dashboard: React.FC = () => {
  // Queries
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>(
    'dashboard-stats',
    getDashboardStats,
    { refetchInterval: 30000 } // Refresh every 30 seconds
  )

  const { data: activity, isLoading: activityLoading } = useQuery(
    'recent-activity',
    getRecentActivity,
    { refetchInterval: 10000 } // Refresh every 10 seconds
  )

  const { data: apiStatus, isLoading: apiLoading } = useQuery(
    'api-status',
    getAPIStatus,
    { refetchInterval: 15000 } // Refresh every 15 seconds
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Visão geral do seu PRFI Protocol
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Sistema Online</span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total de Requests"
          value={stats?.totalRequests || 0}
          icon={<Activity className="w-6 h-6" />}
          trend={+12.5}
          loading={statsLoading}
          color="blue"
        />
        
        <StatsCard
          title="Taxa de Sucesso"
          value={`${stats?.successRate || 0}%`}
          icon={<CheckCircle className="w-6 h-6" />}
          trend={+2.1}
          loading={statsLoading}
          color="green"
        />
        
        <StatsCard
          title="Tempo Médio"
          value={`${stats?.avgResponseTime || 0}ms`}
          icon={<Clock className="w-6 h-6" />}
          trend={-5.3}
          loading={statsLoading}
          color="yellow"
        />
        
        <StatsCard
          title="Tokens Ganhos"
          value={stats?.tokensEarned || 0}
          icon={<DollarSign className="w-6 h-6" />}
          trend={+18.7}
          loading={statsLoading}
          color="purple"
        />
      </div>

      {/* Charts and Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Chart */}
        <div className="lg:col-span-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Performance das APIs
              </h3>
              <div className="flex items-center space-x-2">
                <button className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                  24h
                </button>
                <button className="text-sm text-blue-600 dark:text-blue-400 font-medium">
                  7d
                </button>
                <button className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                  30d
                </button>
              </div>
            </div>
            
            <Chart />
          </motion.div>
        </div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
            Atividade Recente
          </h3>
          
          <RecentActivity data={activity} loading={activityLoading} />
        </motion.div>
      </div>

      {/* API Status and Token Balance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Status das APIs
            </h3>
            <Globe className="w-5 h-5 text-gray-400" />
          </div>
          
          <APIStatus data={apiStatus} loading={apiLoading} />
        </motion.div>

        {/* Token Balance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Saldo de Tokens
            </h3>
            <Zap className="w-5 h-5 text-yellow-500" />
          </div>
          
          <TokenBalance />
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          Ações Rápidas
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center space-x-2 p-4 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
            <TrendingUp className="w-5 h-5" />
            <span>Testar APIs</span>
          </button>
          
          <button className="flex items-center justify-center space-x-2 p-4 bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors">
            <CheckCircle className="w-5 h-5" />
            <span>Deploy Contract</span>
          </button>
          
          <button className="flex items-center justify-center space-x-2 p-4 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors">
            <Zap className="w-5 h-5" />
            <span>Ver Logs</span>
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default Dashboard

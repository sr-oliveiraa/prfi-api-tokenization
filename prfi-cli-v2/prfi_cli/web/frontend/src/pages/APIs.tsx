import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { 
  Globe, 
  Plus, 
  Settings, 
  Play, 
  Pause, 
  Trash2,
  Edit,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Zap
} from 'lucide-react'
import { getAPIStatus, testAPI } from '../services/api'

const APIs: React.FC = () => {
  const [selectedAPI, setSelectedAPI] = useState<string | null>(null)
  const [isAddingAPI, setIsAddingAPI] = useState(false)

  // Query para buscar status das APIs
  const { data: apiStatus, isLoading, refetch } = useQuery({
    queryKey: ['api-status'],
    queryFn: getAPIStatus,
    refetchInterval: 30000, // Atualizar a cada 30 segundos
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'offline':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
      case 'offline':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
      default:
        return 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'
    }
  }

  const handleTestAPI = async (apiName: string, url: string) => {
    try {
      const result = await testAPI({ url, method: 'GET' })
      console.log('Test result:', result)
      // Atualizar dados após teste
      refetch()
    } catch (error) {
      console.error('Test failed:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">APIs</h1>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
                  <div className="h-6 w-6 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                </div>
                <div className="space-y-3">
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Gerenciamento de APIs
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Configure e monitore suas APIs com retry e fallback automático
          </p>
        </div>
        
        <button
          onClick={() => setIsAddingAPI(true)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Adicionar API
        </button>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Globe className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total de APIs
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {apiStatus?.length || 0}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Online
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {apiStatus?.filter(api => api.status === 'online').length || 0}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Com Problemas
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {apiStatus?.filter(api => api.status !== 'online').length || 0}
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6"
        >
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <Zap className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Tempo Médio
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {apiStatus?.length ? 
                  Math.round(apiStatus.reduce((acc, api) => acc + api.response_time, 0) / apiStatus.length) 
                  : 0}ms
              </p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Lista de APIs */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {apiStatus?.map((api, index) => (
          <motion.div
            key={api.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`
              rounded-lg border p-6 transition-all hover:shadow-md cursor-pointer
              ${getStatusColor(api.status)}
              ${selectedAPI === api.name ? 'ring-2 ring-blue-500' : ''}
            `}
            onClick={() => setSelectedAPI(selectedAPI === api.name ? null : api.name)}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {getStatusIcon(api.status)}
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  {api.name}
                </h3>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleTestAPI(api.name, api.url)
                  }}
                  className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                  title="Testar API"
                >
                  <Play className="w-4 h-4" />
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    // Implementar edição
                  }}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  title="Editar"
                >
                  <Edit className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="space-y-2">
              <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                {api.url}
              </p>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500 dark:text-gray-400">
                  Tempo de resposta
                </span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {api.response_time}ms
                </span>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500 dark:text-gray-400">
                  Taxa de sucesso
                </span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {api.success_rate}%
                </span>
              </div>
              
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-3">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${
                    api.success_rate >= 95 
                      ? 'bg-green-500' 
                      : api.success_rate >= 90 
                      ? 'bg-yellow-500' 
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${api.success_rate}%` }}
                ></div>
              </div>
            </div>

            {selectedAPI === api.name && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600"
              >
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 dark:text-gray-400">Última verificação:</span>
                    <span className="text-gray-900 dark:text-white">
                      {new Date(api.last_check * 1000).toLocaleTimeString()}
                    </span>
                  </div>
                  
                  <div className="flex space-x-2 mt-3">
                    <button className="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors">
                      Configurar Retry
                    </button>
                    <button className="flex-1 px-3 py-1 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white text-xs rounded transition-colors">
                      Ver Logs
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Mensagem quando não há APIs */}
      {!apiStatus || apiStatus.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Globe className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Nenhuma API configurada
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Adicione suas primeiras APIs para começar a monitorar
          </p>
          <button
            onClick={() => setIsAddingAPI(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Adicionar Primeira API
          </button>
        </motion.div>
      ) : null}
    </div>
  )
}

export default APIs

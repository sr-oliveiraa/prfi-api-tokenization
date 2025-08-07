import React, { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'

interface ChartProps {
  data?: Array<{
    timestamp: string
    requests: number
    success_rate: number
    response_time: number
  }>
  type?: 'line' | 'area'
  height?: number
}

const Chart: React.FC<ChartProps> = ({ 
  data, 
  type = 'area',
  height = 300 
}) => {
  // Dados de exemplo se não fornecidos
  const defaultData = useMemo(() => [
    { timestamp: '00:00', requests: 120, success_rate: 98.5, response_time: 245 },
    { timestamp: '04:00', requests: 89, success_rate: 97.2, response_time: 312 },
    { timestamp: '08:00', requests: 234, success_rate: 99.1, response_time: 189 },
    { timestamp: '12:00', requests: 456, success_rate: 98.8, response_time: 234 },
    { timestamp: '16:00', requests: 378, success_rate: 99.3, response_time: 198 },
    { timestamp: '20:00', requests: 289, success_rate: 98.9, response_time: 267 },
    { timestamp: '23:59', requests: 156, success_rate: 99.0, response_time: 223 }
  ], [])

  const chartData = data || defaultData

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            {label}
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between mb-1">
              <span 
                className="text-sm"
                style={{ color: entry.color }}
              >
                {entry.name}:
              </span>
              <span className="text-sm font-medium ml-2">
                {entry.name === 'success_rate' 
                  ? `${entry.value}%`
                  : entry.name === 'response_time'
                  ? `${entry.value}ms`
                  : entry.value.toLocaleString()
                }
              </span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  if (type === 'area') {
    return (
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="requestsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="successGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            className="stroke-gray-200 dark:stroke-gray-700"
          />
          
          <XAxis 
            dataKey="timestamp"
            className="text-gray-600 dark:text-gray-400"
            fontSize={12}
          />
          
          <YAxis 
            yAxisId="requests"
            orientation="left"
            className="text-gray-600 dark:text-gray-400"
            fontSize={12}
          />
          
          <YAxis 
            yAxisId="success"
            orientation="right"
            domain={[95, 100]}
            className="text-gray-600 dark:text-gray-400"
            fontSize={12}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Area
            yAxisId="requests"
            type="monotone"
            dataKey="requests"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#requestsGradient)"
            name="Requests"
          />
          
          <Area
            yAxisId="success"
            type="monotone"
            dataKey="success_rate"
            stroke="#10b981"
            strokeWidth={2}
            fill="url(#successGradient)"
            name="Taxa de Sucesso"
          />
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData}>
        <CartesianGrid 
          strokeDasharray="3 3" 
          className="stroke-gray-200 dark:stroke-gray-700"
        />
        
        <XAxis 
          dataKey="timestamp"
          className="text-gray-600 dark:text-gray-400"
          fontSize={12}
        />
        
        <YAxis 
          yAxisId="requests"
          orientation="left"
          className="text-gray-600 dark:text-gray-400"
          fontSize={12}
        />
        
        <YAxis 
          yAxisId="time"
          orientation="right"
          className="text-gray-600 dark:text-gray-400"
          fontSize={12}
        />
        
        <Tooltip content={<CustomTooltip />} />
        
        <Line
          yAxisId="requests"
          type="monotone"
          dataKey="requests"
          stroke="#3b82f6"
          strokeWidth={3}
          dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
          name="Requests"
        />
        
        <Line
          yAxisId="time"
          type="monotone"
          dataKey="response_time"
          stroke="#f59e0b"
          strokeWidth={3}
          dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6, stroke: '#f59e0b', strokeWidth: 2 }}
          name="Tempo de Resposta"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default Chart

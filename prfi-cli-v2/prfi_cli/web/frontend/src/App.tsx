import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import { Toaster } from 'react-hot-toast'

// Layout
import Layout from './components/Layout'

// Pages
import Dashboard from './pages/Dashboard'
import APIs from './pages/APIs'
import Monitoring from './pages/Monitoring'
import Configuration from './pages/Configuration'
import Blockchain from './pages/Blockchain'
import Logs from './pages/Logs'
import Settings from './pages/Settings'

// Styles
import './index.css'

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/apis" element={<APIs />} />
              <Route path="/monitoring" element={<Monitoring />} />
              <Route path="/blockchain" element={<Blockchain />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="/configuration" element={<Configuration />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
          
          {/* Toast notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                duration: 3000,
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#fff',
                },
              },
              error: {
                duration: 5000,
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#fff',
                },
              },
            }}
          />
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App

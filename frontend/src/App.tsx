import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import RoutePlanner from './components/RoutePlanner'
import Dashboard from './components/Dashboard'
import Gamification from './components/Gamification'
import ErrorBoundary from './components/ErrorBoundary'
import { RouteProvider } from './contexts/RouteContext'
import { UserProvider } from './contexts/UserContext'
import { GoogleMapsProvider } from './contexts/GoogleMapsContext'

function App() {
  return (
    <ErrorBoundary>
      <GoogleMapsProvider>
        <UserProvider>
          <RouteProvider>
            <Router future={{ v7_startTransition: true }}>
            <div className="min-h-screen relative overflow-hidden">
              {/* Enhanced Background with Glass Morphism */}
              <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
                {/* Subtle pattern overlay */}
                <div className="absolute inset-0 opacity-20" style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23e0e7ff' fill-opacity='0.1'%3E%3Ccircle cx='20' cy='20' r='1'/%3E%3C/g%3E%3C/svg%3E")`
                }} />

                {/* Floating glass orbs for depth */}
                <div className="absolute top-20 left-10 w-32 h-32 bg-blue-200/20 rounded-full blur-xl animate-pulse-slow" />
                <div className="absolute bottom-20 right-10 w-40 h-40 bg-indigo-200/20 rounded-full blur-xl animate-pulse-slow" style={{ animationDelay: '1s' }} />
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 bg-purple-200/20 rounded-full blur-xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
              </div>

              <motion.main
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="relative z-10"
              >
                <Routes>
                  <Route path="/" element={<RoutePlanner />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/gamification" element={<Gamification />} />
                </Routes>
              </motion.main>
            </div>
            </Router>
          </RouteProvider>
        </UserProvider>
      </GoogleMapsProvider>
    </ErrorBoundary>
  )
}

export default App

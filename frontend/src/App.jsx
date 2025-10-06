import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import HomePage from './pages/HomePage'
import ScannerPage from './pages/ScannerPage'
import DatabasePage from './pages/DatabasePage'
import Navbar from './components/Navbar'
import { ThemeProvider } from './components/theme-provider'

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="smart-campus-theme">
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <Navbar />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/scanner" element={<ScannerPage />} />
            <Route path="/database" element={<DatabasePage />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  )
}

export default App
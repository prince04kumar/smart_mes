import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import HomePage from './pages/HomePage'
import ScannerPage from './pages/ScannerPage'
import DatabasePage from './pages/DatabasePage'
import Navbar from './components/Navbar'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/scanner" element={<ScannerPage />} />
          <Route path="/database" element={<DatabasePage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
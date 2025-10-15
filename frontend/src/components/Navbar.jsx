import { Link, useLocation } from 'react-router-dom'
import { Home, Scan, Database, LogOut, User } from 'lucide-react'
import { ThemeToggle } from './theme-toggle'
import { useAuth } from '../context/AuthContext'
import { Button } from './ui/button'

function Navbar() {
  const location = useLocation()
  const { user, logout } = useAuth()

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/scanner', label: 'ID Scanner', icon: Scan },
    { path: '/database', label: 'Database', icon: Database },
  ]

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout()
    }
  }

  return (
    <nav className="sticky top-0 z-50 bg-card/95 backdrop-blur-lg shadow-lg border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Institute Name */}
          <Link to="/" className="flex items-center space-x-3 group">
            <img 
              src="/collegeLOgo.jpg" 
              alt="Institute Logo" 
              className="h-11 w-11 rounded-full object-cover border-2 border-primary/20 group-hover:border-primary/40 transition-all"
            />
            <div>
              <h1 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors">
                Smart Campus
              </h1>
              <p className="text-xs text-muted-foreground">
                Document Management System
              </p>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-primary text-primary-foreground shadow-md scale-105'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent hover:scale-105'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.label}
                </Link>
              )
            })}
          </div>

          {/* User Info and Actions */}
          <div className="flex items-center space-x-3">
            <div className="hidden lg:flex items-center space-x-3 px-4 py-2 rounded-lg bg-muted/50">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
                <User className="w-4 h-4 text-primary-foreground" />
              </div>
              <div className="text-sm">
                <div className="font-semibold text-foreground">{user?.name}</div>
                <div className="text-xs text-muted-foreground">{user?.scan_count || 0} scans completed</div>
              </div>
            </div>
            <ThemeToggle />
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={handleLogout}
              className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden md:inline ml-2">Logout</span>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden pb-4">
          <div className="flex flex-col space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-3" />
                  {item.label}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
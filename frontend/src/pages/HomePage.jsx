import { Link } from 'react-router-dom'
import { Scan, Database, Users, Shield, Zap, Clock } from 'lucide-react'

function HomePage() {
  const features = [
    {
      icon: Scan,
      title: 'Smart ID Scanning',
      description: 'Advanced OCR technology powered by AWS Textract for accurate text extraction from Docs',
      color: 'blue'
    },
    {
      icon: Users,
      title: 'Student Database',
      description: 'Comprehensive database management with intelligent search and person identification',
      color: 'green'
    },
    {
      icon: Shield,
      title: 'Security Notifications',
      description: 'Instant email notifications with scanned documents for enhanced campus security',
      color: 'purple'
    },
    {
      icon: Zap,
      title: 'Real-time Processing',
      description: 'Lightning-fast processing with Redis caching for optimal performance',
      color: 'yellow'
    },
    {
      icon: Clock,
      title: 'Audit Trail',
      description: 'Complete scan history tracking with timestamps for administrative oversight',
      color: 'red'
    },
    {
      icon: Database,
      title: 'Cloud Integration',
      description: 'MongoDB cloud database with Docker containerization for scalability',
      color: 'indigo'
    }
  ]

  const stats = [
    { label: 'Students Registered', value: '2,547', change: '+12%' },
    { label: 'Scans Today', value: '156', change: '+8%' },
    { label: 'Active Sessions', value: '23', change: '+4%' },
    { label: 'System Uptime', value: '99.9%', change: 'Stable' }
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white">
        <div className="absolute inset-0 bg-black/20"></div>
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'url(/college_front.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        ></div>
        
        <div className="relative container mx-auto px-4 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <div className="mb-8">
              <img 
                src="/collegeLOgo.jpg" 
                alt="Institute Logo" 
                className="h-20 w-20 mx-auto rounded-full border-4 border-white/20 mb-4"
              />
              <h1 className="text-5xl md:text-6xl font-bold mb-4">
                Smart Campus
                <span className="block text-blue-300 text-3xl md:text-4xl mt-2">
                  ID Management System
                </span>
              </h1>
              <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
                Advanced AI-powered identity verification system for modern educational institutions. 
                Secure, fast, and intelligent student identification.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/scanner"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200 flex items-center justify-center"
              >
                <Scan className="w-6 h-6 mr-2" />
                Start Scanning
              </Link>
              <Link
                to="/database"
                className="bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200 flex items-center justify-center"
              >
                <Database className="w-6 h-6 mr-2" />
                Manage Database
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl">
                <div className="text-3xl font-bold text-gray-800 mb-2">{stat.value}</div>
                <div className="text-gray-600 mb-2">{stat.label}</div>
                <div className={`text-sm font-medium ${
                  stat.change.includes('+') ? 'text-green-600' : 'text-blue-600'
                }`}>
                  {stat.change}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gray-50 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-800 mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our comprehensive ID management system combines cutting-edge AI technology 
              with intuitive design to deliver unparalleled campus security and efficiency.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              const colorClasses = {
                blue: 'bg-blue-100 text-blue-600',
                green: 'bg-green-100 text-green-600',
                purple: 'bg-purple-100 text-purple-600',
                yellow: 'bg-yellow-100 text-yellow-600',
                red: 'bg-red-100 text-red-600',
                indigo: 'bg-indigo-100 text-indigo-600'
              }
              
              return (
                <div key={index} className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <div className={`w-14 h-14 rounded-lg ${colorClasses[feature.color]} flex items-center justify-center mb-6`}>
                    <Icon className="w-7 h-7" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to modernize your campus security?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Join leading educational institutions using Smart Campus ID Management
          </p>
          <Link
            to="/scanner"
            className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-4 rounded-lg font-semibold text-lg transition-colors duration-200 inline-flex items-center"
          >
            <Scan className="w-6 h-6 mr-2" />
            Get Started Now
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <img 
                  src="/collegeLOgo.jpg" 
                  alt="Institute Logo" 
                  className="h-8 w-8 rounded-full"
                />
                <h3 className="text-xl font-bold">Smart Campus</h3>
              </div>
              <p className="text-gray-400">
                Advanced ID management system powered by AI and cloud technology.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li>AI-Powered Scanning</li>
                <li>Real-time Notifications</li>
                <li>Database Management</li>
                <li>Security Analytics</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">System Status</h4>
              <div className="space-y-2 text-gray-400">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  API Server: Online
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  Database: Connected
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  Cache: Active
                </div>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Smart Campus ID Management System. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
import { Link } from 'react-router-dom'
import { Scan, Database, Users, Shield, Zap, Clock } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import useDocumentTitle from '../hooks/useDocumentTitle'

function HomePage() {
  useDocumentTitle('Home');
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
      <section className="relative bg-gradient-to-br from-primary via-primary/90 to-primary/80 text-primary-foreground">
        <div className="absolute inset-0 bg-background/10"></div>
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
                className="h-20 w-20 mx-auto rounded-full border-4 border-primary-foreground/20 mb-4"
              />
              <h1 className="text-5xl md:text-6xl font-bold mb-4 text-primary-foreground">
                Smart Campus
                <span className="block text-primary-foreground/80 text-3xl md:text-4xl mt-2">
                  ID Management System
                </span>
              </h1>
              <p className="text-xl md:text-2xl text-primary-foreground/90 mb-8 max-w-3xl mx-auto">
                Advanced AI-powered identity verification system for modern educational institutions. 
                Secure, fast, and intelligent student identification.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" asChild>
                <Link to="/scanner" className="flex items-center">
                  <Scan className="w-6 h-6 mr-2" />
                  Start Scanning
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to="/database" className="flex items-center">
                  <Database className="w-6 h-6 mr-2" />
                  Manage Database
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-muted/30 py-16">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <Card key={index} className="text-center hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="text-3xl font-bold text-foreground mb-2">{stat.value}</div>
                  <div className="text-muted-foreground mb-2">{stat.label}</div>
                  <div className={`text-sm font-medium ${
                    stat.change.includes('+') ? 'text-emerald-600' : 'text-primary'
                  }`}>
                    {stat.change}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-background py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Our comprehensive ID management system combines cutting-edge AI technology 
              with intuitive design to deliver unparalleled campus security and efficiency.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              const colorClasses = {
                blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400',
                green: 'bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400',
                purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400',
                yellow: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/20 dark:text-yellow-400',
                red: 'bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400',
                indigo: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/20 dark:text-indigo-400'
              }
              
              return (
                <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                  <CardHeader>
                    <div className={`w-14 h-14 rounded-lg ${colorClasses[feature.color]} flex items-center justify-center mb-2`}>
                      <Icon className="w-7 h-7" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="leading-relaxed">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to modernize your campus security?
          </h2>
          <p className="text-xl mb-8 text-primary-foreground/90">
            Join leading educational institutions using Smart Campus ID Management
          </p>
          <Button size="lg" variant="secondary" asChild>
            <Link to="/scanner" className="inline-flex items-center">
              <Scan className="w-6 h-6 mr-2" />
              Get Started Now
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <img 
                  src="/collegeLOgo.jpg" 
                  alt="Institute Logo" 
                  className="h-8 w-8 rounded-full"
                />
                <h3 className="text-xl font-bold text-foreground">Smart Campus</h3>
              </div>
              <p className="text-muted-foreground">
                Advanced ID management system powered by AI and cloud technology.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4 text-foreground">Features</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li>AI-Powered Scanning</li>
                <li>Real-time Notifications</li>
                <li>Database Management</li>
                <li>Security Analytics</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4 text-foreground">System Status</h4>
              <div className="space-y-2 text-muted-foreground">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></div>
                  API Server: Online
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></div>
                  Database: Connected
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2"></div>
                  Cache: Active
                </div>
              </div>
            </div>
          </div>
          <div className="border-t border-border mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2025 Smart Campus ID Management System. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
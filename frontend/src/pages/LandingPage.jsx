import { Link } from 'react-router-dom'
import { Scan, Database, Shield, Zap, Cloud, Award, CheckCircle, ArrowRight, LogIn, UserPlus } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { ThemeToggle } from '../components/theme-toggle'
import useDocumentTitle from '../hooks/useDocumentTitle'

function LandingPage() {
  useDocumentTitle('Welcome to Smart Campus');

  const features = [
    {
      icon: Scan,
      title: 'Smart Document Scanning',
      description: 'Advanced OCR technology powered by AWS Textract for accurate text extraction from any document',
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Database,
      title: 'Cloud Database',
      description: 'Secure Supabase PostgreSQL database with real-time synchronization and backup',
      gradient: 'from-green-500 to-emerald-500'
    },
    {
      icon: Shield,
      title: 'Enterprise Security',
      description: 'JWT authentication, bcrypt encryption, and role-based access control',
      gradient: 'from-purple-500 to-pink-500'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Real-time processing with intelligent caching for optimal performance',
      gradient: 'from-yellow-500 to-orange-500'
    },
    {
      icon: Cloud,
      title: 'Cloud Deployment',
      description: 'Deployed on AWS EC2 and Vercel for maximum reliability and scalability',
      gradient: 'from-indigo-500 to-blue-500'
    },
    {
      icon: Award,
      title: 'AI-Powered',
      description: 'Machine learning algorithms for intelligent person identification and fuzzy name matching',
      gradient: 'from-red-500 to-rose-500'
    }
  ]

  const benefits = [
    'Instant document scanning and analysis',
    'Automated person identification',
    'Real-time email notifications',
    'Complete audit trail and history',
    'Multi-user support with permissions',
    'Mobile-responsive interface',
    'Dark mode support',
    '99.9% uptime guarantee'
  ]

  const stats = [
    { value: '10K+', label: 'Documents Scanned' },
    { value: '500+', label: 'Active Users' },
    { value: '99.9%', label: 'Accuracy Rate' },
    { value: '24/7', label: 'Support Available' }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-card/80 backdrop-blur-lg border-b border-border shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <img 
                src="/collegeLOgo.jpg" 
                alt="Smart Campus Logo" 
                className="h-10 w-10 rounded-full object-cover border-2 border-primary/20"
              />
              <div>
                <h1 className="text-xl font-bold text-foreground">Smart Campus</h1>
                <p className="text-xs text-muted-foreground">Document Management System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <ThemeToggle />
              <Button variant="ghost" asChild>
                <Link to="/login" className="flex items-center">
                  <LogIn className="w-4 h-4 mr-2" />
                  Login
                </Link>
              </Button>
              <Button asChild>
                <Link to="/login?signup=true" className="flex items-center">
                  <UserPlus className="w-4 h-4 mr-2" />
                  Sign Up
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-primary/10 to-background"></div>
        <div 
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }}
        ></div>
        
        <div className="relative container mx-auto px-4 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
              <Zap className="w-4 h-4 mr-2" />
              AI-Powered Document Management
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary via-primary/80 to-primary/60">
              Welcome to Smart Campus
            </h1>
            
            <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
              Revolutionary document scanning and identity management system powered by AWS Textract and AI. 
              Transform how your institution handles documents and verifies identities.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Button size="lg" className="text-lg h-14 px-8" asChild>
                <Link to="/login?signup=true" className="flex items-center">
                  <UserPlus className="w-5 h-5 mr-2" />
                  Get Started Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" className="text-lg h-14 px-8" asChild>
                <Link to="/login" className="flex items-center">
                  <LogIn className="w-5 h-5 mr-2" />
                  Sign In
                </Link>
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {stats.map((stat, index) => (
                <div key={index} className="bg-card rounded-lg p-6 border border-border shadow-sm">
                  <div className="text-3xl md:text-4xl font-bold text-primary mb-2">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to manage documents and identities efficiently
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <Card key={index} className="relative overflow-hidden group hover:shadow-xl transition-all duration-300 border-2 hover:border-primary/50">
                  <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${feature.gradient}`}></div>
                  <CardHeader>
                    <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-4xl md:text-5xl font-bold mb-6">Why Choose Smart Campus?</h2>
                <p className="text-xl text-muted-foreground mb-8">
                  Built with cutting-edge technology and designed for modern educational institutions.
                </p>
                <div className="space-y-4">
                  {benefits.map((benefit, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
                      <span className="text-lg">{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary/5 rounded-3xl transform rotate-3"></div>
                <div className="relative bg-card rounded-2xl p-8 shadow-2xl border border-border">
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-muted-foreground">System Status</span>
                      <span className="flex items-center text-green-500">
                        <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                        Online
                      </span>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Server Performance</span>
                          <span className="text-primary font-medium">98%</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-green-500 to-emerald-500 w-[98%]"></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Database Health</span>
                          <span className="text-primary font-medium">100%</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 w-full"></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>API Response Time</span>
                          <span className="text-primary font-medium">45ms</span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 w-[92%]"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary to-primary/80 text-primary-foreground">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to Get Started?</h2>
          <p className="text-xl mb-12 max-w-2xl mx-auto opacity-90">
            Join hundreds of institutions already using Smart Campus to streamline their document management
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="text-lg h-14 px-8" asChild>
              <Link to="/login?signup=true" className="flex items-center">
                <UserPlus className="w-5 h-5 mr-2" />
                Create Free Account
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg h-14 px-8 bg-primary-foreground/10 hover:bg-primary-foreground/20 border-primary-foreground/20" asChild>
              <Link to="/login" className="flex items-center">
                <LogIn className="w-5 h-5 mr-2" />
                Sign In to Dashboard
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <img 
                src="/collegeLOgo.jpg" 
                alt="Smart Campus Logo" 
                className="h-10 w-10 rounded-full object-cover"
              />
              <div>
                <h3 className="font-bold">Smart Campus</h3>
                <p className="text-sm text-muted-foreground">Document Management System</p>
              </div>
            </div>
            <div className="text-center md:text-right text-sm text-muted-foreground">
              <p>&copy; 2025 Smart Campus. All rights reserved.</p>
              <p className="mt-1">Powered by AWS Textract & Supabase</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage

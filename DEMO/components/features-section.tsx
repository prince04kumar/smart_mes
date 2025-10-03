"use client"

import { motion, useScroll, useTransform } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Zap, Shield, Clock, Database, Brain, Mail } from "lucide-react"
import { useRef } from "react"

const features = [
  {
    icon: Brain,
    title: "AI-Powered Recognition",
    description: "Advanced machine learning algorithms identify document owners with 98%+ accuracy",
    color: "from-primary to-accent",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Process and identify documents in under 3 seconds with our optimized AI pipeline",
    color: "from-accent to-primary",
  },
  {
    icon: Database,
    title: "Secure Database",
    description: "Encrypted storage with instant lookup across thousands of records",
    color: "from-primary to-accent",
  },
  {
    icon: Mail,
    title: "Instant Delivery",
    description: "Automatically send documents via email with customizable templates",
    color: "from-accent to-primary",
  },
  {
    icon: Shield,
    title: "Privacy First",
    description: "GDPR compliant with end-to-end encryption and secure data handling",
    color: "from-primary to-accent",
  },
  {
    icon: Clock,
    title: "Save Time",
    description: "Reduce manual document sorting time by 95% with automated identification",
    color: "from-accent to-primary",
  },
]

export function FeaturesSection() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  })

  const y = useTransform(scrollYProgress, [0, 1], [100, -100])

  return (
    <section ref={ref} className="py-32 px-4 relative overflow-hidden">
      <motion.div style={{ y }} className="absolute inset-0 grid-pattern opacity-30" />

      <div className="container mx-auto max-w-7xl relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center space-y-4 mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground">Powerful Features</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto text-pretty">
            Everything you need to manage documents efficiently in your institute
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="p-6 space-y-4 h-full hover:border-primary/50 transition-colors group">
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} p-0.5`}>
                  <div className="w-full h-full rounded-lg bg-card flex items-center justify-center">
                    <feature.icon className="w-6 h-6 text-primary" />
                  </div>
                </div>

                <h3 className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>

                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

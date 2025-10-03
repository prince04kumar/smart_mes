"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Loader2, Sparkles, Search, Database } from "lucide-react"

interface ProcessingSectionProps {
  fileName: string
}

export function ProcessingSection({ fileName }: ProcessingSectionProps) {
  const steps = [
    { icon: Sparkles, label: "Analyzing document", delay: 0 },
    { icon: Search, label: "Extracting information", delay: 0.5 },
    { icon: Database, label: "Searching database", delay: 1 },
  ]

  return (
    <section className="py-20 px-4">
      <div className="container mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="p-12 text-center space-y-8 glow-effect">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 border-2 border-primary/20"
            >
              <Loader2 className="w-10 h-10 text-primary" />
            </motion.div>

            <div className="space-y-2">
              <h2 className="text-3xl font-bold text-foreground">Processing Document</h2>
              <p className="text-muted-foreground text-lg">{fileName}</p>
            </div>

            <div className="space-y-4 max-w-md mx-auto">
              {steps.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: step.delay, duration: 0.5 }}
                  className="flex items-center gap-4 p-4 rounded-lg bg-secondary/50 border border-border"
                >
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <step.icon className="w-5 h-5 text-primary" />
                  </div>
                  <span className="text-foreground font-medium">{step.label}</span>
                  <motion.div
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}
                    className="ml-auto"
                  >
                    <Loader2 className="w-5 h-5 text-primary animate-spin" />
                  </motion.div>
                </motion.div>
              ))}
            </div>

            <div className="flex items-center justify-center gap-2">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY }}
                className="w-2 h-2 rounded-full bg-primary"
              />
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, delay: 0.2 }}
                className="w-2 h-2 rounded-full bg-primary"
              />
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, delay: 0.4 }}
                className="w-2 h-2 rounded-full bg-primary"
              />
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}

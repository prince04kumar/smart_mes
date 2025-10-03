"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Mail, Phone, Building, CheckCircle2, Send, RotateCcw, Sparkles } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface ResultsSectionProps {
  person: any
  document: File | null
  onReset: () => void
}

export function ResultsSection({ person, document, onReset }: ResultsSectionProps) {
  const [isSending, setIsSending] = useState(false)
  const [emailSubject, setEmailSubject] = useState("Found Document - Please Collect")
  const [emailMessage, setEmailMessage] = useState(
    `Dear ${person.name},\n\nWe have found a document that belongs to you. Please find it attached to this email.\n\nBest regards,\nDocument Management System`,
  )
  const { toast } = useToast()

  const handleSendEmail = async () => {
    setIsSending(true)

    // Simulate sending email
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setIsSending(false)
    toast({
      title: "Email Sent Successfully!",
      description: `Document sent to ${person.email}`,
    })

    setTimeout(() => {
      onReset()
    }, 2000)
  }

  return (
    <section className="py-20 px-4">
      <div className="container mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          {/* Success Header */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="text-center space-y-4"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-accent/10 border-2 border-accent/20">
              <CheckCircle2 className="w-8 h-8 text-accent" />
            </div>
            <h2 className="text-3xl font-bold text-foreground">Owner Identified!</h2>
            <p className="text-muted-foreground text-lg">
              AI has successfully identified the document owner with {person.confidence}% confidence
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Person Details Card */}
            <motion.div initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
              <Card className="p-6 space-y-6 h-full">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  <h3 className="text-xl font-semibold text-foreground">Identified Person</h3>
                </div>

                <div className="flex items-start gap-4">
                  <Avatar className="w-20 h-20 border-2 border-primary/20">
                    <AvatarImage src={person.image || "/placeholder.svg"} alt={person.name} />
                    <AvatarFallback className="bg-primary/10 text-primary text-xl">
                      {person.name
                        .split(" ")
                        .map((n: string) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 space-y-2">
                    <h4 className="text-2xl font-bold text-foreground">{person.name}</h4>
                    <Badge variant="secondary" className="font-mono">
                      {person.id}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-3 pt-4 border-t border-border">
                  <div className="flex items-center gap-3 text-foreground">
                    <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                      <Building className="w-5 h-5 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Department</p>
                      <p className="font-medium">{person.department}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-foreground">
                    <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                      <Mail className="w-5 h-5 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Email</p>
                      <p className="font-medium font-mono text-sm">{person.email}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-foreground">
                    <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                      <Phone className="w-5 h-5 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Phone</p>
                      <p className="font-medium font-mono">{person.phone}</p>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-border">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">AI Confidence</span>
                    <span className="text-lg font-bold text-accent">{person.confidence}%</span>
                  </div>
                  <div className="mt-2 h-2 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${person.confidence}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                      className="h-full bg-gradient-to-r from-accent to-primary"
                    />
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Send Email Card */}
            <motion.div initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}>
              <Card className="p-6 space-y-6 h-full">
                <div className="flex items-center gap-2">
                  <Send className="w-5 h-5 text-primary" />
                  <h3 className="text-xl font-semibold text-foreground">Send Document</h3>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="recipient" className="text-foreground">
                      Recipient
                    </Label>
                    <Input
                      id="recipient"
                      value={person.email}
                      disabled
                      className="font-mono bg-secondary text-foreground"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="subject" className="text-foreground">
                      Subject
                    </Label>
                    <Input
                      id="subject"
                      value={emailSubject}
                      onChange={(e) => setEmailSubject(e.target.value)}
                      className="bg-background text-foreground"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="message" className="text-foreground">
                      Message
                    </Label>
                    <Textarea
                      id="message"
                      value={emailMessage}
                      onChange={(e) => setEmailMessage(e.target.value)}
                      rows={8}
                      className="bg-background text-foreground resize-none"
                    />
                  </div>

                  <div className="p-3 rounded-lg bg-secondary/50 border border-border">
                    <p className="text-sm text-muted-foreground">
                      <strong className="text-foreground">Attachment:</strong> {document?.name}
                    </p>
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button onClick={handleSendEmail} disabled={isSending} className="flex-1" size="lg">
                    {isSending ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                        >
                          <Send className="w-5 h-5 mr-2" />
                        </motion.div>
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5 mr-2" />
                        Send Email
                      </>
                    )}
                  </Button>

                  <Button onClick={onReset} variant="outline" size="lg" disabled={isSending}>
                    <RotateCcw className="w-5 h-5" />
                  </Button>
                </div>
              </Card>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

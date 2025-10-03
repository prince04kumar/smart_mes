"use client"

import { useState } from "react"
import { motion, useScroll, useTransform } from "framer-motion"
import { HeroSection } from "@/components/hero-section"
import { UploadSection } from "@/components/upload-section"
import { ProcessingSection } from "@/components/processing-section"
import { ResultsSection } from "@/components/results-section"
import { FeaturesSection } from "@/components/features-section"

export default function Home() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [identifiedPerson, setIdentifiedPerson] = useState<any>(null)

  const { scrollYProgress } = useScroll()
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0])

  const handleFileUpload = (file: File) => {
    setUploadedFile(file)
    setIsProcessing(true)

    // Simulate AI processing
    setTimeout(() => {
      setIsProcessing(false)
      setIdentifiedPerson({
        name: "Dr. Sarah Johnson",
        id: "FAC-2024-1234",
        department: "Computer Science",
        email: "sarah.johnson@institute.edu",
        phone: "+1 (555) 123-4567",
        image: "/professional-woman-portrait.png",
        confidence: 98.5,
      })
    }, 3000)
  }

  const handleReset = () => {
    setUploadedFile(null)
    setIsProcessing(false)
    setIdentifiedPerson(null)
  }

  return (
    <main className="min-h-screen bg-background">
      <motion.div style={{ opacity }} className="fixed inset-0 grid-pattern pointer-events-none" />

      <HeroSection />

      <div className="relative z-10">
        {!uploadedFile && !identifiedPerson && <UploadSection onFileUpload={handleFileUpload} />}

        {isProcessing && <ProcessingSection fileName={uploadedFile?.name || ""} />}

        {identifiedPerson && !isProcessing && (
          <ResultsSection person={identifiedPerson} document={uploadedFile} onReset={handleReset} />
        )}

        <FeaturesSection />
      </div>
    </main>
  )
}

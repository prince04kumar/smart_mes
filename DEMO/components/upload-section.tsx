"use client"

import type React from "react"

import { useCallback, useState } from "react"
import { motion } from "framer-motion"
import { Upload, FileText, Camera } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface UploadSectionProps {
  onFileUpload: (file: File) => void
}

export function UploadSection({ onFileUpload }: UploadSectionProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const file = e.dataTransfer.files[0]
      if (file && (file.type.includes("image") || file.type.includes("pdf"))) {
        onFileUpload(file)
      }
    },
    [onFileUpload],
  )

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      onFileUpload(file)
    }
  }

  return (
    <section className="py-20 px-4">
      <div className="container mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <Card
            className={`relative overflow-hidden transition-all duration-300 ${
              isDragging ? "border-primary bg-primary/5 glow-effect" : "border-border"
            }`}
            onDragOver={(e) => {
              e.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <div className="p-12 text-center space-y-6">
              <motion.div
                animate={isDragging ? { scale: 1.1 } : { scale: 1 }}
                className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 border-2 border-primary/20"
              >
                <Upload className="w-10 h-10 text-primary" />
              </motion.div>

              <div className="space-y-2">
                <h2 className="text-3xl font-bold text-foreground">Upload Document</h2>
                <p className="text-muted-foreground text-lg">Drag and drop your document here, or click to browse</p>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button
                  size="lg"
                  className="relative overflow-hidden group"
                  onClick={() => document.getElementById("file-input")?.click()}
                >
                  <FileText className="w-5 h-5 mr-2" />
                  Choose File
                  <input
                    id="file-input"
                    type="file"
                    accept="image/*,.pdf"
                    className="hidden"
                    onChange={handleFileInput}
                  />
                </Button>

                <Button
                  size="lg"
                  variant="outline"
                  className="relative overflow-hidden group bg-transparent"
                  onClick={() => document.getElementById("camera-input")?.click()}
                >
                  <Camera className="w-5 h-5 mr-2" />
                  Take Photo
                  <input
                    id="camera-input"
                    type="file"
                    accept="image/*"
                    capture="environment"
                    className="hidden"
                    onChange={handleFileInput}
                  />
                </Button>
              </div>

              <p className="text-sm text-muted-foreground">Supports: JPG, PNG, PDF • Max size: 10MB</p>
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}

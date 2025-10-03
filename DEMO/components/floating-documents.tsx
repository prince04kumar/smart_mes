"use client"

import { useRef } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { Float, MeshDistortMaterial } from "@react-three/drei"
import type * as THREE from "three"

function Document({ position, rotation }: { position: [number, number, number]; rotation: [number, number, number] }) {
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = rotation[1] + Math.sin(state.clock.elapsedTime * 0.3) * 0.1
      meshRef.current.rotation.x = rotation[0] + Math.cos(state.clock.elapsedTime * 0.2) * 0.1
    }
  })

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <mesh ref={meshRef} position={position} rotation={rotation}>
        <boxGeometry args={[1.5, 2, 0.05]} />
        <MeshDistortMaterial color="#6366f1" opacity={0.3} transparent distort={0.3} speed={2} />
      </mesh>
    </Float>
  )
}

export function FloatingDocuments() {
  return (
    <div className="absolute inset-0 opacity-40">
      <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <Document position={[-3, 2, 0]} rotation={[0.2, 0.3, 0]} />
        <Document position={[3, -1, -2]} rotation={[-0.2, -0.3, 0.1]} />
        <Document position={[0, 1, -3]} rotation={[0.1, 0, -0.2]} />
        <Document position={[-2, -2, -1]} rotation={[0.3, 0.2, 0.1]} />
      </Canvas>
    </div>
  )
}

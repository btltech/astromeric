import React, { useMemo, useRef, useState, useEffect } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sparkles, Stars, Html } from '@react-three/drei';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface PlanetPos {
  name: string;
  x: float;
  y: float;
  z: float;
  distance: float;
  color: string;
}

function Planet({ pos, isMobile }: { pos: PlanetPos; isMobile: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const orbitalScale = 4.0; // Scale AU to Three.js units

  useFrame((_state) => {
    if (meshRef.current) {
      // Gentle self-rotation
      meshRef.current.rotation.y += 0.01;
    }
  });

  // Size logic
  const size = useMemo(() => {
    if (pos.name === 'Sun') return 0.8;
    if (pos.name === 'Jupiter' || pos.name === 'Saturn') return 0.4;
    if (pos.name === 'Moon') return 0.1;
    return 0.2;
  }, [pos.name]);

  return (
    <group position={[pos.x * orbitalScale, pos.z * orbitalScale, pos.y * orbitalScale]}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[size, 32, 32]} />
        <meshStandardMaterial
          color={pos.color}
          emissive={pos.color}
          emissiveIntensity={pos.name === 'Sun' ? 2 : 0.5}
        />
      </mesh>
      {pos.name === 'Sun' && <pointLight intensity={2} distance={20} color={pos.color} />}
      {!isMobile && (
        <Html distanceFactor={10}>
          <div className="planet-label" style={{ color: pos.color }}>
            {pos.name}
          </div>
        </Html>
      )}
    </group>
  );
}

function Planetarium({ isMobile }: { isMobile: boolean }) {
  const [planets, setPlanets] = useState<PlanetPos[]>([]);

  useEffect(() => {
    const fetchPlanets = async () => {
      try {
        const res = await fetch(`${API_BASE}/v2/sky/planets`);
        const data = await res.json();
        if (data.status === 'success') {
          setPlanets(data.data);
        }
      } catch (err) {
        console.error('Failed to fetch planetarium data', err);
      }
    };
    fetchPlanets();
    // Refresh every 10 minutes (planets move slow, but Moon moves faster)
    const interval = setInterval(fetchPlanets, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <group rotation={[Math.PI / 8, 0, 0]}>
      {planets.map((p) => (
        <Planet key={p.name} pos={p} isMobile={isMobile} />
      ))}
    </group>
  );
}

const ELEMENT_STYLES: Record<
  string,
  {
    primary: string;
    secondary: string;
    speed: number;
    rotationSpeed: number;
    floatIntensity: number;
    glow: string;
  }
> = {
  Fire: {
    primary: '#ff5e57',
    secondary: '#ffc048',
    speed: 3,
    rotationSpeed: 0.1,
    floatIntensity: 1,
    glow: '#ff9472',
  },
  Water: {
    primary: '#4bcffa',
    secondary: '#575fcf',
    speed: 1.5,
    rotationSpeed: 0.02,
    floatIntensity: 2,
    glow: '#6dd5ed',
  },
  Earth: {
    primary: '#05c46b',
    secondary: '#ffd32a',
    speed: 1,
    rotationSpeed: 0.01,
    floatIntensity: 0.5,
    glow: '#88d498',
  },
  Air: {
    primary: '#d2dae2',
    secondary: '#0fb9b1',
    speed: 4,
    rotationSpeed: 0.08,
    floatIntensity: 1.5,
    glow: '#c8e0ff',
  },
  Default: {
    primary: '#88c0d0',
    secondary: '#bf616a',
    speed: 2,
    rotationSpeed: 0.05,
    floatIntensity: 0.6,
    glow: '#88c0d0',
  },
};

function ZodiacRing({
  element = 'Default',
  isMobile = false,
  tilt = 0,
}: {
  element?: string;
  isMobile?: boolean;
  tilt?: number;
}) {
  const meshRef1 = useRef<THREE.Mesh>(null);
  const meshRef2 = useRef<THREE.Mesh>(null);
  const materialRef1 = useRef<THREE.MeshStandardMaterial>(null);
  const materialRef2 = useRef<THREE.MeshStandardMaterial>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  const style = useMemo(() => ELEMENT_STYLES[element] || ELEMENT_STYLES['Default'], [element]);

  useFrame((state, delta) => {
    const time = state.clock.elapsedTime;
    const pulseFactor = Math.max(style.floatIntensity, 0.5);
    const wobble = style.rotationSpeed;
    const tiltClamped = Math.max(-0.35, Math.min(0.35, tilt));

    if (meshRef1.current) {
      meshRef1.current.rotation.z += delta * style.rotationSpeed;
      meshRef1.current.rotation.x =
        Math.sin(time * 0.3) * 0.15 + Math.sin(time * style.speed * 0.2) * 0.05 + tiltClamped;
      const pulse = 1 + Math.sin(time * 0.5 * style.speed) * (0.02 * pulseFactor);
      meshRef1.current.scale.setScalar(pulse);
      meshRef1.current.rotation.y = Math.sin(time * 0.6) * (0.05 * wobble) + tiltClamped * 0.5;
    }
    if (meshRef2.current) {
      meshRef2.current.rotation.z -= delta * (style.rotationSpeed * 0.8);
      meshRef2.current.rotation.y =
        Math.cos(time * 0.2) * 0.1 + Math.cos(time * style.speed * 0.2) * 0.05 + tiltClamped;
      const pulse = 1 + Math.cos(time * 0.4 * style.speed) * (0.02 * pulseFactor);
      meshRef2.current.scale.setScalar(pulse);
      meshRef2.current.rotation.x = Math.cos(time * 0.5) * (0.04 * wobble) + tiltClamped * 0.3;
    }

    if (glowRef.current) {
      const glowPulse = 1.2 + Math.sin(time * 0.7) * 0.05;
      glowRef.current.scale.setScalar(glowPulse);
    }

    if (materialRef1.current) {
      materialRef1.current.color.lerp(new THREE.Color(style.primary), delta * 2);
      materialRef1.current.emissive.lerp(new THREE.Color(style.primary), delta * 2);
    }
    if (materialRef2.current) {
      materialRef2.current.color.lerp(new THREE.Color(style.secondary), delta * 2);
      materialRef2.current.emissive.lerp(new THREE.Color(style.secondary), delta * 2);
    }
  });

  return (
    <Float speed={style.speed} rotationIntensity={0.4} floatIntensity={style.floatIntensity}>
      <mesh ref={meshRef1} position={[0, 0, -2]}>
        <torusGeometry args={[3.5, 0.02, 64, 100]} />
        <meshStandardMaterial
          ref={materialRef1}
          color="#88c0d0"
          emissive="#88c0d0"
          emissiveIntensity={0.5}
          wireframe
        />
      </mesh>

      <mesh ref={meshRef2} rotation={[0, 0, 1]}>
        <torusGeometry args={[2.5, 0.015, 64, 100]} />
        <meshStandardMaterial
          ref={materialRef2}
          color="#bf616a"
          emissive="#bf616a"
          emissiveIntensity={0.3}
          wireframe
        />
      </mesh>

      <mesh ref={glowRef} position={[0, 0, -3]} rotation={[Math.PI / 2, 0, 0]}>
        <circleGeometry args={[5, 64]} />
        <meshBasicMaterial color={style.glow} transparent opacity={0.15} />
      </mesh>

      <Sparkles
        count={(() => {
          const base = element === 'Air' || element === 'Fire' ? 80 : 40;
          return isMobile ? Math.max(20, Math.floor(base * 0.5)) : base;
        })()}
        scale={isMobile ? 4 : 6}
        size={isMobile ? 3 : element === 'Earth' ? 6 : 4}
        speed={style.speed * 0.2}
        opacity={0.5}
        color={style.primary}
      />
    </Float>
  );
}

export function CosmicBackground({ element }: { element?: string }) {
  const reduceMotion =
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) {
    return <div className="cosmic-bg static" aria-hidden="true" />;
  }

  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;
  const lowPowerDevice =
    typeof navigator !== 'undefined' &&
    /Mobi|Android/i.test(navigator.userAgent) &&
    (((navigator as never as { deviceMemory?: number }).deviceMemory ?? 4) <= 3 ||
      (navigator.hardwareConcurrency ?? 4) <= 2);

  if (lowPowerDevice) {
    return <div className="cosmic-bg static" aria-hidden="true" />;
  }

  const starCount = isMobile ? 2000 : 6000;
  const starFactor = isMobile ? 3 : 4;
  const [keyboardTilt, setKeyboardTilt] = useState(0);
  const [pointerTilt, setPointerTilt] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(e.key)) {
      e.preventDefault();
    }
    if (e.key === 'ArrowLeft') setKeyboardTilt((t) => Math.max(-0.35, t - 0.05));
    if (e.key === 'ArrowRight') setKeyboardTilt((t) => Math.min(0.35, t + 0.05));
    if (e.key === 'ArrowUp') setKeyboardTilt((t) => Math.min(0.35, t + 0.02));
    if (e.key === 'ArrowDown') setKeyboardTilt((t) => Math.max(-0.35, t - 0.02));
    if (e.key === ' ') setKeyboardTilt(0);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    setPointerTilt(Math.max(-0.35, Math.min(0.35, x * 0.7)));
  };

  return (
    <div
      className="cosmic-bg"
      role="img"
      aria-label="Animated cosmic background showing your element. Use arrow keys or drag to tilt the rings."
      aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown Space"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onPointerMove={handlePointerMove}
      onPointerLeave={() => setPointerTilt(0)}
      onPointerUp={() => setPointerTilt(0)}
    >
      <Canvas camera={{ position: [0, 0, 5] }}>
        <fog attach="fog" args={['#0b0c15', 5, 20]} />
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <Stars
          radius={100}
          depth={50}
          count={starCount}
          factor={starFactor}
          saturation={0}
          fade
          speed={1}
        />
        <Planetarium isMobile={isMobile} />
        <ZodiacRing element={element} isMobile={isMobile} tilt={keyboardTilt + pointerTilt} />
      </Canvas>
    </div>
  );
}

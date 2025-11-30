import React, { useState, useRef, useEffect, useMemo } from 'react';
import { createRoot } from 'react-dom/client';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { Stars, Float, Sparkles } from '@react-three/drei';
import './styles.css';

// --- CONFIGURATION ---
// In production, this would point to your Railway URL
// Casting import.meta to any to avoid TypeScript error about 'env' property
const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
// Force simulation for the preview environment since Python backend isn't running in browser
const FORCE_SIMULATION = false; 

// --- TYPES ---
interface Profile {
  id: number;
  name: string;
  date_of_birth: string;
}

interface PredictionData {
  scope: string;
  date: string;
  summary?: { headline?: string; top_factors?: any };
  sections: Array<{ title: string; rating?: number; highlights: string[]; affirmation?: string }>;
  numerology?: any;
  element?: string;
  sign?: string;
  life_path_number?: number;
}

interface NumerologyProfile {
  life_path: { number: number; meaning: string };
  expression: { number: number; meaning: string };
  soul_urge: { number: number; meaning: string };
  personality: { number: number; meaning: string };
  maturity: { number: number; meaning: string };
  personal_year: { number: number; meaning: string };
  personal_month: { number: number; meaning: string };
  personal_day: { number: number; meaning: string };
  pinnacles: Array<{ number: number; meaning: string }>;
  challenges: Array<{ number: number; meaning: string }>;
}

interface CompatibilityResult {
  overall_score: number;
  astrology: {
    element_score: number;
    modality_score: number;
    analysis: string;
  };
  numerology: {
    life_path_score: number;
    expression_score: number;
    analysis: string;
  };
  strengths: string[];
  challenges: string[];
  advice: string;
}

// --- CLIENT-SIDE SIMULATION ENGINE (FALLBACK) ---
const simulateBackend = async (profileId: number, scope: string): Promise<PredictionData> => {
  await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay

  // Mock profile data
  const profiles = [
    { id: 1, name: "John Doe", date_of_birth: "1990-01-01" },
    { id: 2, name: "Jane Smith", date_of_birth: "1985-05-15" }
  ];
  const profile = profiles.find(p => p.id === profileId) || profiles[0];
  const date = new Date(profile.date_of_birth);
  const day = date.getDate();
  const month = date.getMonth() + 1;
  
  // Basic Astrology Logic
  let sign = "Capricorn";
  if ((month === 1 && day >= 20) || (month === 2 && day <= 18)) sign = "Aquarius";
  // ... (same as before)

  const elements: Record<string, string> = {
    Aries: "Fire", Leo: "Fire", Sagittarius: "Fire",
    Taurus: "Earth", Virgo: "Earth", Capricorn: "Earth",
    Gemini: "Air", Libra: "Air", Aquarius: "Air",
    Cancer: "Water", Scorpio: "Water", Pisces: "Water"
  };

  // Basic Numerology Logic
  const sumDigits = (n: number): number => {
    while (n > 9 && n !== 11 && n !== 22 && n !== 33) {
      n = n.toString().split('').reduce((a, b) => a + parseInt(b), 0);
    }
    return n;
  };
  const lifePath = sumDigits(date.getFullYear() + month + day);
  const nameNum = sumDigits(profile.name.toLowerCase().replace(/[^a-z]/g, '').split('').reduce((acc, char) => acc + (char.charCodeAt(0) - 96), 0));

  // Pseudo-random seed
  const luckyNums = Array.from({length: 4}, () => Math.floor(Math.random() * 99) + 1);
  const colors = ["#FF5252", "#448AFF", "#69F0AE", "#FFD740", "#E040FB", "#536DFE"];

  const tracks = {
    general: `Overview: Embrace the flow of ${elements[sign]} energy as a ${sign}.`,
    love: "In matters of the heart, communication is key. Be open to new possibilities.",
    money: "Financial prospects involve careful planning. Make informed decisions.",
    health: "Wellbeing focuses on balance. Prioritize rest and nourishment.",
    spiritual: "Personal growth calls for reflection. Trust your intuition."
  };

  const ratings = {
    general: Math.floor(Math.random() * 2) + 3,
    love: Math.floor(Math.random() * 2) + 3,
    money: Math.floor(Math.random() * 3) + 2,
    health: Math.floor(Math.random() * 2) + 4,
    spiritual: Math.floor(Math.random() * 2) + 3
  };

  return {
    scope,
    date: new Date().toISOString().split('T')[0],
    summary: { headline: `Today's cosmic alignment favors ${sign} with Life Path ${lifePath} energy.` },
    sections: [
      { title: "Overview", rating: ratings.general, highlights: [tracks.general] },
      { title: "Love & Relationships", rating: ratings.love, highlights: [tracks.love] },
      { title: "Work & Money", rating: ratings.money, highlights: [tracks.money] },
      { title: "Emotional / Spiritual", rating: ratings.spiritual, highlights: [tracks.spiritual] },
      { title: "Actions & Advice", highlights: ["Trust your intuition; it knows the way."] },
    ],
    sign,
    life_path_number: lifePath,
    element: elements[sign] || "Unknown",
  };
};

// --- 3D COMPONENTS ---

const ELEMENT_STYLES: Record<string, { 
  primary: string; 
  secondary: string; 
  speed: number; 
  rotationSpeed: number;
  floatIntensity: number; 
  glow: string;
}> = {
  Fire: { 
    primary: '#ff5e57', 
    secondary: '#ffc048', 
    speed: 3, 
    rotationSpeed: 0.1, 
    floatIntensity: 1,
    glow: '#ff9472'
  },
  Water: { 
    primary: '#4bcffa', 
    secondary: '#575fcf', 
    speed: 1.5, 
    rotationSpeed: 0.02, 
    floatIntensity: 2,
    glow: '#6dd5ed'
  },
  Earth: { 
    primary: '#05c46b', 
    secondary: '#ffd32a', 
    speed: 1, 
    rotationSpeed: 0.01, 
    floatIntensity: 0.5,
    glow: '#88d498'
  },
  Air: { 
    primary: '#d2dae2', 
    secondary: '#0fb9b1', 
    speed: 4, 
    rotationSpeed: 0.08, 
    floatIntensity: 1.5,
    glow: '#c8e0ff'
  },
  Default: { 
    primary: '#88c0d0', 
    secondary: '#bf616a', 
    speed: 2, 
    rotationSpeed: 0.05, 
    floatIntensity: 0.6,
    glow: '#88c0d0'
  }
};

function ZodiacRing({ element = 'Default', isMobile = false, tilt = 0 }: { element?: string, isMobile?: boolean, tilt?: number }) {
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
      // Rotation logic
      meshRef1.current.rotation.z += delta * style.rotationSpeed;
      // Add dynamic 'wobble' to rotation X based on element speed
      meshRef1.current.rotation.x = Math.sin(time * 0.3) * 0.15 + Math.sin(time * style.speed * 0.2) * 0.05 + tiltClamped;
      
      // Subtle pulsing effect linked to element speed
      const pulse = 1 + Math.sin(time * 0.5 * style.speed) * (0.02 * pulseFactor);
      meshRef1.current.scale.setScalar(pulse);
      meshRef1.current.rotation.y = Math.sin(time * 0.6) * (0.05 * wobble) + tiltClamped * 0.5;
    }
    if (meshRef2.current) {
      meshRef2.current.rotation.z -= delta * (style.rotationSpeed * 0.8);
      // Add dynamic 'wobble' to rotation Y based on element speed
      meshRef2.current.rotation.y = Math.cos(time * 0.2) * 0.1 + Math.cos(time * style.speed * 0.2) * 0.05 + tiltClamped;

      // Subtle pulsing effect (offset phase)
      const pulse = 1 + Math.cos(time * 0.4 * style.speed) * (0.02 * pulseFactor);
      meshRef2.current.scale.setScalar(pulse);
      meshRef2.current.rotation.x = Math.cos(time * 0.5) * (0.04 * wobble) + tiltClamped * 0.3;
    }

    if (glowRef.current) {
      const glowPulse = 1.2 + Math.sin(time * 0.7) * 0.05;
      glowRef.current.scale.setScalar(glowPulse);
    }

    // Smooth color transition
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
      {/* Outer Ring */}
      <mesh ref={meshRef1} position={[0, 0, -2]}>
        <torusGeometry args={[3.5, 0.02, 64, 100]} />
        <meshStandardMaterial ref={materialRef1} color="#88c0d0" emissive="#88c0d0" emissiveIntensity={0.5} wireframe />
      </mesh>
      
      {/* Inner Ring */}
      <mesh ref={meshRef2} rotation={[0, 0, 1]}>
         <torusGeometry args={[2.5, 0.015, 64, 100]} />
         <meshStandardMaterial ref={materialRef2} color="#bf616a" emissive="#bf616a" emissiveIntensity={0.3} wireframe />
      </mesh>

      {/* Glow backplate influenced by element */}
      <mesh ref={glowRef} position={[0,0,-3]} rotation={[Math.PI / 2, 0, 0]}>
        <circleGeometry args={[5, 64]} />
        <meshBasicMaterial color={style.glow} transparent opacity={0.15} />
      </mesh>

      {/* Magical Particles */}
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

function CosmicBackground({ element }: { element?: string }) {
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;
  const starCount = isMobile ? 2000 : 6000;
  const starFactor = isMobile ? 3 : 4;
  const [keyboardTilt, setKeyboardTilt] = useState(0);
  const [pointerTilt, setPointerTilt] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(e.key)) {
      e.preventDefault();
    }
    if (e.key === 'ArrowLeft') setKeyboardTilt(t => Math.max(-0.35, t - 0.05));
    if (e.key === 'ArrowRight') setKeyboardTilt(t => Math.min(0.35, t + 0.05));
    if (e.key === 'ArrowUp') setKeyboardTilt(t => Math.min(0.35, t + 0.02));
    if (e.key === 'ArrowDown') setKeyboardTilt(t => Math.max(-0.35, t - 0.02));
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
        <Stars radius={100} depth={50} count={starCount} factor={starFactor} saturation={0} fade speed={1} />
        <ZodiacRing element={element} isMobile={isMobile} tilt={keyboardTilt + pointerTilt} />
      </Canvas>
    </div>
  );
}

// --- UI COMPONENTS ---

function FortuneForm({ onSubmit, isLoading }: { onSubmit: (d: any) => void, isLoading: boolean }) {
  const [formData, setFormData] = useState({
    name: '',
    date_of_birth: '',
    time_of_birth: '',
    place_of_birth: ''
  });
  const [errors, setErrors] = useState<{[k:string]:string}>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Client-side validation
    const newErrors: {[k:string]:string} = {};
    if (!formData.name.trim()) newErrors.name = 'Please enter your full name.';
    if (!formData.date_of_birth) newErrors.date_of_birth = 'Please provide your date of birth.';
    else {
      const dob = new Date(formData.date_of_birth);
      const today = new Date();
      if (dob > today) newErrors.date_of_birth = 'Date of birth cannot be in the future.';
    }
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;
    onSubmit(formData);
  };

  return (
    <div className="card">
      <h2 className="form-title">Enter Your Details</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Full Name</label>
          <input 
            type="text" 
            required 
            placeholder="e.g. Jane Doe"
            value={formData.name}
            onChange={e => setFormData({...formData, name: e.target.value})}
          />
            {errors.name && <div className="error-text">{errors.name}</div>}
        </div>
        <div className="form-group">
          <label>Date of Birth</label>
          <input 
            type="date" 
            required 
            value={formData.date_of_birth}
            onChange={e => setFormData({...formData, date_of_birth: e.target.value})}
          />
            {errors.date_of_birth && <div className="error-text">{errors.date_of_birth}</div>}
        </div>
        <div className="form-group">
          <label>Time of Birth (Optional)</label>
          <input 
            type="time" 
            value={formData.time_of_birth}
            onChange={e => setFormData({...formData, time_of_birth: e.target.value})}
          />
        </div>
        <div className="form-group">
          <label>Place of Birth (Optional)</label>
          <input 
            type="text" 
            placeholder="City, Country"
            value={formData.place_of_birth}
            onChange={e => setFormData({...formData, place_of_birth: e.target.value})}
          />
        </div>
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? 'Reading the Stars...' : 'Get Today\'s Prediction'}
        </button>
      </form>
    </div>
  );
}

// small helper styles for inline errors
const styleEl = document.createElement('style');
styleEl.innerHTML = `.error-text{color:#ffbcbc;font-size:0.85rem;margin-top:6px}`;
document.head.appendChild(styleEl);

function FortuneResult({ data, onReset }: { data: PredictionData, onReset: () => void }) {
  const RatingBar = ({ value, label }: { value: number, label: string }) => (
    <div className="rating-row">
      <span>{label}</span>
      <div className="stars">
        {[...Array(5)].map((_, i) => (
          <span key={i} className={i < value ? "filled" : ""}>★</span>
        ))}
      </div>
    </div>
  );

  return (
    <div className="card">
      <div className="header-badge">
        {data.element === 'Fire' && '🔥'}
        {data.element === 'Water' && '💧'}
        {data.element === 'Air' && '🌬️'}
        {data.element === 'Earth' && '🌱'}
      </div>
      <h1 style={{textAlign: 'center', marginBottom: '0.5rem'}}>{data.scope.charAt(0).toUpperCase() + data.scope.slice(1)} Reading</h1>
      {data.sign && data.life_path_number && (
        <h3 style={{textAlign: 'center', color: '#88c0d0', fontWeight: 300, marginBottom: '2rem'}}>
          {data.sign} • Life Path {data.life_path_number}
        </h3>
      )}

      {data.summary?.headline && (
        <div className="tldr-box">
          <strong>TL;DR:</strong> {data.summary.headline}
        </div>
      )}

      {data.sections && data.sections.length > 0 && (
        <div className="tracks-grid">
          {data.sections.map((section, idx) => (
            <div key={idx} className="track-item">
              <h3>{section.title}</h3>
              {section.highlights.map((h, i) => <p key={i}>{h}</p>)}
              {section.rating ? <RatingBar label="Energy" value={section.rating} /> : null}
              {section.affirmation && <p className="affirmation-text">{section.affirmation}</p>}
            </div>
          ))}
        </div>
      )}

      <button onClick={onReset} className="btn-secondary">Back to Profiles</button>
    </div>
  );
}

function App() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<number | null>(null);
  const [selectedScope, setSelectedScope] = useState<string>("daily");
  const [result, setResult] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [view, setView] = useState<'reading' | 'numerology' | 'compatibility' | 'learn'>('reading');
  const [numerologyProfile, setNumerologyProfile] = useState<NumerologyProfile | null>(null);
  const [compatibilityResult, setCompatibilityResult] = useState<CompatibilityResult | null>(null);
  const [compareProfile, setCompareProfile] = useState<number | null>(null);
  const [glossary, setGlossary] = useState<any>(null);
  const [zodiacPage, setZodiacPage] = useState(0);
  const [numerologyPage, setNumerologyPage] = useState(0);
  const ZODIAC_PAGE_SIZE = 6;
  const NUM_PAGE_SIZE = 8;

  const zodiacEntries = useMemo(() => {
    if (!glossary?.zodiac) return [];
    return Object.entries(glossary.zodiac).slice(0, (zodiacPage + 1) * ZODIAC_PAGE_SIZE);
  }, [glossary, zodiacPage]);

  const numerologyEntries = useMemo(() => {
    if (!glossary?.numerology) return [];
    return Object.entries(glossary.numerology).slice(0, (numerologyPage + 1) * NUM_PAGE_SIZE);
  }, [glossary, numerologyPage]);

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      const response = await fetch(`${API_URL}/profiles`);
      if (response.ok) {
        const data = await response.json();
        setProfiles(data);
      }
    } catch (err) {
      // Fallback to simulation
    }
  };

  const fetchNumerologyProfile = async () => {
    if (!selectedProfile) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetchWithRetry(`${API_URL}/numerology/profile/${selectedProfile}`);
      if (response.ok) {
        const data = await response.json();
        setNumerologyProfile(data);
      } else {
        throw new Error('Failed to load numerology profile');
      }
    } catch (err: any) {
      setError(friendlyError(err, 'Failed to load numerology profile.'));
    } finally {
      setLoading(false);
    }
  };

  const fetchCompatibility = async () => {
    if (!selectedProfile || !compareProfile) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetchWithRetry(`${API_URL}/compatibility/combined`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile_id_1: selectedProfile,
          profile_id_2: compareProfile,
          relationship_type: 'romantic'
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setCompatibilityResult(data);
      } else {
        throw new Error('Failed to calculate compatibility');
      }
    } catch (err: any) {
      setError(friendlyError(err, 'Failed to calculate compatibility.'));
    } finally {
      setLoading(false);
    }
  };

  const fetchGlossary = async () => {
    if (glossary) return; // Already loaded
    setLoading(true);
    try {
      const [zodiacRes, numRes] = await Promise.all([
        fetch(`${API_URL}/learn/zodiac`),
        fetch(`${API_URL}/learn/numerology`)
      ]);
      const zodiac = zodiacRes.ok ? await zodiacRes.json() : {};
      const numerology = numRes.ok ? await numRes.json() : {};
      setGlossary({ zodiac, numerology });
    } catch (err) {
      // Silent fail
    } finally {
      setLoading(false);
    }
  };

  const createProfile = async (formData: any) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetchWithRetry(`${API_URL}/profiles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        const data = await response.json();
        setSelectedProfile(data.id);
        await fetchProfiles();
        setShowCreateForm(false);
      } else {
        throw new Error('Failed to create profile');
      }
    } catch (err: any) {
      setError(friendlyError(err, 'Failed to create profile.'));
    } finally {
      setLoading(false);
    }
  };

  const getPrediction = async () => {
    if (!selectedProfile) return;
    setLoading(true);
    setError('');
    try {
      if (FORCE_SIMULATION) {
        const data = await simulateBackend(selectedProfile, selectedScope);
        setResult(data);
      } else {
        const response = await fetchWithRetry(`${API_URL}/forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ profile_id: selectedProfile, scope: selectedScope }),
        }, 2);
        if (!response.ok) {
          let detail = 'The stars are cloudy... please try again.';
          try {
            const errJson = await response.json();
            detail = errJson.detail || detail;
          } catch (_) {}
          throw new Error(detail);
        }
        const data: PredictionData = await response.json();
        // If legacy /reading is used elsewhere, still accept engine_v2 field
        const forecastData = (data as any).engine_v2 ? (data as any).engine_v2 : data;
        setResult(forecastData);
      }
    } catch (err: any) {
      console.error(err);
      setError(friendlyError(err, 'We lost the connection to the cosmos. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  // Fetch with simple retry/backoff
  async function fetchWithRetry(input: RequestInfo, init?: RequestInit, retries = 2, backoff = 300) {
    let attempt = 0;
    let lastError: any = null;
    while (true) {
      try {
        const res = await fetch(input, init);
        if (attempt > 0) setError('');
        return res;
      } catch (err) {
        lastError = err;
        if (attempt >= retries) throw err;
        setError('Connection lost—retrying...');
        await new Promise(r => setTimeout(r, backoff * Math.pow(2, attempt)));
        attempt++;
      }
    }
  }

  const friendlyError = (err: any, fallback: string) => {
    if (err?.message?.includes('Failed to fetch')) return 'Connection lost—retrying failed. Check your network.';
    return err?.message || fallback;
  };

  return (
    <div className="app-container">
      <CosmicBackground element={result?.element} />
      
      <div className="content-wrapper">
        <header>
          <h1 className="logo">ASTRO<span>NUMEROLOGY</span></h1>
        </header>

        {error && <div className="error-banner">{error}</div>}

        {/* Main Navigation */}
        {selectedProfile && !result && (
          <div className="main-nav">
            <button className={view === 'reading' ? 'nav-btn active' : 'nav-btn'} onClick={() => setView('reading')}>📖 Reading</button>
            <button className={view === 'numerology' ? 'nav-btn active' : 'nav-btn'} onClick={() => { setView('numerology'); fetchNumerologyProfile(); }}>🔢 Numerology</button>
            <button className={view === 'compatibility' ? 'nav-btn active' : 'nav-btn'} onClick={() => setView('compatibility')}>💕 Compatibility</button>
            <button
              className={view === 'learn' ? 'nav-btn active' : 'nav-btn'}
              onClick={() => { setView('learn'); setZodiacPage(0); setNumerologyPage(0); fetchGlossary(); }}
            >📚 Learn</button>
          </div>
        )}

        {!result ? (
          <div>
            {/* Profile Selection */}
            <div className="card">
              <h2>Select or Create Profile</h2>
              {profiles.length > 0 && (
                <div className="form-group">
                  <label>Select Profile</label>
                  <select value={selectedProfile || ''} onChange={e => setSelectedProfile(Number(e.target.value))}>
                    <option value="">Choose...</option>
                    {profiles.map(p => <option key={p.id} value={p.id}>{p.name} ({p.date_of_birth})</option>)}
                  </select>
                </div>
              )}
              <button onClick={() => setShowCreateForm(!showCreateForm)} className="btn-secondary">
                {showCreateForm ? 'Cancel' : 'Create New Profile'}
              </button>
            </div>
            {showCreateForm && <FortuneForm onSubmit={createProfile} isLoading={loading} />}

            {/* Reading View */}
            {selectedProfile && view === 'reading' && (
              <div className="card">
                <h2>Select Scope</h2>
                <div className="tabs">
                  {["daily", "weekly", "monthly"].map(scope => (
                    <button
                      key={scope}
                      className={selectedScope === scope ? "tab active" : "tab"}
                      onClick={() => setSelectedScope(scope)}
                    >
                      {scope.charAt(0).toUpperCase() + scope.slice(1)}
                    </button>
                  ))}
                </div>
                <button onClick={getPrediction} className="btn-primary" disabled={loading}>
                  {loading ? 'Reading...' : `Get ${selectedScope.charAt(0).toUpperCase() + selectedScope.slice(1)} Reading`}
                </button>
              </div>
            )}

            {/* Numerology Profile View */}
            {selectedProfile && view === 'numerology' && (
              <div className="card">
                <h2>🔢 Your Numerology Profile</h2>
                {numerologyProfile ? (
                  <div className="numerology-grid">
                    <div className="num-card">
                      <h4>Life Path</h4>
                      <div className="num-value">{numerologyProfile.life_path.number}</div>
                      <p>{numerologyProfile.life_path.meaning}</p>
                    </div>
                    <div className="num-card">
                      <h4>Expression</h4>
                      <div className="num-value">{numerologyProfile.expression.number}</div>
                      <p>{numerologyProfile.expression.meaning}</p>
                    </div>
                    <div className="num-card">
                      <h4>Soul Urge</h4>
                      <div className="num-value">{numerologyProfile.soul_urge.number}</div>
                      <p>{numerologyProfile.soul_urge.meaning}</p>
                    </div>
                    <div className="num-card">
                      <h4>Personality</h4>
                      <div className="num-value">{numerologyProfile.personality.number}</div>
                      <p>{numerologyProfile.personality.meaning}</p>
                    </div>
                    <div className="num-card">
                      <h4>Maturity</h4>
                      <div className="num-value">{numerologyProfile.maturity.number}</div>
                      <p>{numerologyProfile.maturity.meaning}</p>
                    </div>
                    <div className="num-card highlight">
                      <h4>Personal Year</h4>
                      <div className="num-value">{numerologyProfile.personal_year.number}</div>
                      <p>{numerologyProfile.personal_year.meaning}</p>
                    </div>
                    <div className="num-card">
                      <h4>Personal Month</h4>
                      <div className="num-value">{numerologyProfile.personal_month.number}</div>
                      <p>{numerologyProfile.personal_month.meaning}</p>
                    </div>
                    <div className="num-card">
                      <h4>Personal Day</h4>
                      <div className="num-value">{numerologyProfile.personal_day.number}</div>
                      <p>{numerologyProfile.personal_day.meaning}</p>
                    </div>
                    {numerologyProfile.pinnacles && numerologyProfile.pinnacles.length > 0 && (
                      <div className="num-card wide">
                        <h4>Life Pinnacles</h4>
                        <div className="pinnacles-row">
                          {numerologyProfile.pinnacles.map((p, i) => (
                            <div key={i} className="pinnacle">
                              <span className="pinnacle-num">{p.number}</span>
                              <span className="pinnacle-label">Phase {i+1}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {numerologyProfile.challenges && numerologyProfile.challenges.length > 0 && (
                      <div className="num-card wide">
                        <h4>Life Challenges</h4>
                        <div className="pinnacles-row">
                          {numerologyProfile.challenges.map((c, i) => (
                            <div key={i} className="pinnacle challenge">
                              <span className="pinnacle-num">{c.number}</span>
                              <span className="pinnacle-label">Challenge {i+1}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p style={{textAlign: 'center', color: '#888'}}>Loading numerology profile...</p>
                )}
              </div>
            )}

            {/* Compatibility View */}
            {selectedProfile && view === 'compatibility' && (
              <div className="card">
                <h2>💕 Compatibility Check</h2>
                <p style={{textAlign: 'center', marginBottom: '1rem', color: '#aaa'}}>
                  Compare your cosmic alignment with another profile
                </p>
                <div className="form-group">
                  <label>Compare With</label>
                  <select value={compareProfile || ''} onChange={e => setCompareProfile(Number(e.target.value))}>
                    <option value="">Choose a profile...</option>
                    {profiles.filter(p => p.id !== selectedProfile).map(p => (
                      <option key={p.id} value={p.id}>{p.name} ({p.date_of_birth})</option>
                    ))}
                  </select>
                </div>
                <button 
                  onClick={fetchCompatibility} 
                  className="btn-primary" 
                  disabled={loading || !compareProfile}
                >
                  {loading ? 'Calculating...' : 'Calculate Compatibility'}
                </button>

                {compatibilityResult && (
                  <div className="compatibility-result">
                    <div className="compat-score">
                      <div className="score-circle" style={{
                        background: `conic-gradient(#88c0d0 ${compatibilityResult.overall_score}%, #2d3748 0)`
                      }}>
                        <span>{compatibilityResult.overall_score}%</span>
                      </div>
                      <h3>Overall Compatibility</h3>
                    </div>

                    <div className="compat-breakdown">
                      <div className="compat-section">
                        <h4>🌟 Astrology</h4>
                        <div className="score-bar">
                          <div className="bar-fill" style={{width: `${(compatibilityResult.astrology.element_score + compatibilityResult.astrology.modality_score) / 2}%`}}></div>
                        </div>
                        <p>{compatibilityResult.astrology.analysis}</p>
                      </div>
                      <div className="compat-section">
                        <h4>🔢 Numerology</h4>
                        <div className="score-bar">
                          <div className="bar-fill" style={{width: `${(compatibilityResult.numerology.life_path_score + compatibilityResult.numerology.expression_score) / 2}%`}}></div>
                        </div>
                        <p>{compatibilityResult.numerology.analysis}</p>
                      </div>
                    </div>

                    <div className="compat-lists">
                      <div className="compat-list strengths">
                        <h4>💪 Strengths</h4>
                        <ul>{compatibilityResult.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                      </div>
                      <div className="compat-list challenges">
                        <h4>⚡ Challenges</h4>
                        <ul>{compatibilityResult.challenges.map((c, i) => <li key={i}>{c}</li>)}</ul>
                      </div>
                    </div>

                    <div className="compat-advice">
                      <strong>💡 Advice:</strong> {compatibilityResult.advice}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Learn/Glossary View */}
            {selectedProfile && view === 'learn' && (
              <div className="card">
                <h2>📚 Learn</h2>
                {glossary ? (
                  <div className="learn-content">
                    <div className="learn-section">
                      <h3>♈ Zodiac Signs</h3>
                      <div className="glossary-grid">
                        {zodiacEntries.map(([sign, info]: [string, any]) => (
                          <div key={sign} className="glossary-item">
                            <h4>{info.symbol} {sign}</h4>
                            <p className="dates">{info.dates}</p>
                            <p className="element">{info.element} • {info.modality}</p>
                            <p>{info.description?.slice(0, 100)}...</p>
                          </div>
                        ))}
                      </div>
                      {glossary?.zodiac && zodiacEntries.length < Object.keys(glossary.zodiac).length && (
                        <div className="load-more">
                          <button className="btn-secondary" onClick={() => setZodiacPage(z => z + 1)}>Load more signs</button>
                        </div>
                      )}
                    </div>
                    <div className="learn-section">
                      <h3>🔢 Life Path Numbers</h3>
                      <div className="glossary-grid">
                        {numerologyEntries.map(([key, info]: [string, any]) => (
                          <div key={key} className="glossary-item">
                            <h4>{key}</h4>
                            <p>{info.meaning?.slice(0, 100) || info.description?.slice(0, 100)}...</p>
                          </div>
                        ))}
                      </div>
                      {glossary?.numerology && numerologyEntries.length < Object.keys(glossary.numerology).length && (
                        <div className="load-more">
                          <button className="btn-secondary" onClick={() => setNumerologyPage(n => n + 1)}>Load more numbers</button>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <p style={{textAlign: 'center', color: '#888'}}>Loading glossary...</p>
                )}
              </div>
            )}
          </div>
        ) : (
          <FortuneResult data={result} onReset={() => setResult(null)} />
        )}
      </div>
      {FORCE_SIMULATION && <div className="demo-mode-badge">Simulation Mode</div>}
      {loading && (
        <div className="loader-overlay" aria-live="polite">
          <div className="spinner" aria-hidden="true"></div>
          <span>Consulting the stars...</span>
        </div>
      )}
    </div>
  );
}

const root = createRoot(document.getElementById('root')!);
root.render(<App />);

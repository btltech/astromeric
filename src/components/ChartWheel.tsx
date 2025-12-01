/**
 * ChartWheel.tsx
 * Interactive SVG natal chart visualization
 */
import React, { useMemo, useState } from 'react';
import { motion } from 'framer-motion';

interface Planet {
  name: string;
  sign: string;
  degree: number;
  house: number;
}

interface Aspect {
  planet1: string;
  planet2: string;
  aspect: string;
  orb: number;
}

interface ChartData {
  planets: Record<string, Planet>;
  houses: Record<string, { cusp: number; sign: string }>;
  aspects: Aspect[];
  ascendant?: { sign: string; degree: number };
  midheaven?: { sign: string; degree: number };
}

interface Props {
  chartData: ChartData;
  size?: number;
  interactive?: boolean;
}

const ZODIAC_SIGNS = [
  { name: 'Aries', symbol: '♈', color: '#ff6b6b' },
  { name: 'Taurus', symbol: '♉', color: '#4ecdc4' },
  { name: 'Gemini', symbol: '♊', color: '#ffe66d' },
  { name: 'Cancer', symbol: '♋', color: '#95e1d3' },
  { name: 'Leo', symbol: '♌', color: '#f9ca24' },
  { name: 'Virgo', symbol: '♍', color: '#a29bfe' },
  { name: 'Libra', symbol: '♎', color: '#fd79a8' },
  { name: 'Scorpio', symbol: '♏', color: '#6c5ce7' },
  { name: 'Sagittarius', symbol: '♐', color: '#e17055' },
  { name: 'Capricorn', symbol: '♑', color: '#636e72' },
  { name: 'Aquarius', symbol: '♒', color: '#74b9ff' },
  { name: 'Pisces', symbol: '♓', color: '#81ecec' },
];

const PLANET_SYMBOLS: Record<string, { symbol: string; color: string }> = {
  Sun: { symbol: '☉', color: '#f9ca24' },
  Moon: { symbol: '☽', color: '#dfe6e9' },
  Mercury: { symbol: '☿', color: '#a29bfe' },
  Venus: { symbol: '♀', color: '#fd79a8' },
  Mars: { symbol: '♂', color: '#ff6b6b' },
  Jupiter: { symbol: '♃', color: '#e17055' },
  Saturn: { symbol: '♄', color: '#636e72' },
  Uranus: { symbol: '♅', color: '#74b9ff' },
  Neptune: { symbol: '♆', color: '#6c5ce7' },
  Pluto: { symbol: '♇', color: '#2d3436' },
};

const ASPECT_COLORS: Record<string, string> = {
  conjunction: '#f9ca24',
  opposition: '#ff6b6b',
  trine: '#4ecdc4',
  square: '#e17055',
  sextile: '#74b9ff',
};

function getSignIndex(signName: string): number {
  return ZODIAC_SIGNS.findIndex((s) => s.name.toLowerCase() === signName.toLowerCase());
}

function degreeToAngle(sign: string, degree: number): number {
  const signIndex = getSignIndex(sign);
  if (signIndex === -1) return 0;
  // Each sign is 30 degrees, start from Aries at top (270 degrees in SVG)
  const totalDegree = signIndex * 30 + degree;
  // Convert to SVG angle (0 at right, counter-clockwise)
  return (270 - totalDegree + 360) % 360;
}

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const angleRad = (angleDeg * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(angleRad),
    y: cy - r * Math.sin(angleRad),
  };
}

export function ChartWheel({ chartData, size = 500, interactive = true }: Props) {
  const [hoveredPlanet, setHoveredPlanet] = useState<string | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);

  const cx = size / 2;
  const cy = size / 2;
  const outerRadius = size / 2 - 20;
  const zodiacWidth = 40;
  const innerRadius = outerRadius - zodiacWidth;
  const houseRadius = innerRadius - 10;
  const planetRadius = houseRadius - 40;
  const aspectRadius = planetRadius - 30;

  // Calculate planet positions
  const planetPositions = useMemo(() => {
    const positions: Record<string, { x: number; y: number; angle: number }> = {};

    if (!chartData?.planets) return positions;

    Object.entries(chartData.planets).forEach(([name, planet]) => {
      const angle = degreeToAngle(planet.sign, planet.degree);
      const pos = polarToCartesian(cx, cy, planetRadius, angle);
      positions[name] = { ...pos, angle };
    });

    return positions;
  }, [chartData, cx, cy, planetRadius]);

  // Draw zodiac segments
  const zodiacSegments = useMemo(() => {
    return ZODIAC_SIGNS.map((sign, i) => {
      const startAngle = 270 - i * 30;
      const endAngle = startAngle - 30;

      const start1 = polarToCartesian(cx, cy, outerRadius, startAngle);
      const end1 = polarToCartesian(cx, cy, outerRadius, endAngle);
      const start2 = polarToCartesian(cx, cy, innerRadius, endAngle);
      const end2 = polarToCartesian(cx, cy, innerRadius, startAngle);

      const d = [
        `M ${start1.x} ${start1.y}`,
        `A ${outerRadius} ${outerRadius} 0 0 1 ${end1.x} ${end1.y}`,
        `L ${start2.x} ${start2.y}`,
        `A ${innerRadius} ${innerRadius} 0 0 0 ${end2.x} ${end2.y}`,
        'Z',
      ].join(' ');

      // Symbol position
      const midAngle = startAngle - 15;
      const symbolPos = polarToCartesian(cx, cy, (outerRadius + innerRadius) / 2, midAngle);

      return { sign, d, symbolPos, startAngle, endAngle };
    });
  }, [cx, cy, outerRadius, innerRadius]);

  // Draw house lines
  const houseLines = useMemo(() => {
    if (!chartData?.houses) return [];

    return Object.entries(chartData.houses).map(([houseNum, house]) => {
      const angle = degreeToAngle(house.sign, house.cusp);
      const inner = polarToCartesian(cx, cy, aspectRadius, angle);
      const outer = polarToCartesian(cx, cy, innerRadius, angle);
      const labelPos = polarToCartesian(cx, cy, houseRadius, angle);

      return { houseNum, inner, outer, labelPos, angle };
    });
  }, [chartData, cx, cy, aspectRadius, innerRadius, houseRadius]);

  // Draw aspect lines
  const aspectLines = useMemo(() => {
    if (!chartData?.aspects || !planetPositions) return [];

    return chartData.aspects
      .filter((asp) => planetPositions[asp.planet1] && planetPositions[asp.planet2])
      .map((asp, i) => {
        const p1 = planetPositions[asp.planet1];
        const p2 = planetPositions[asp.planet2];
        const color = ASPECT_COLORS[asp.aspect] || '#888';
        const opacity = Math.max(0.3, 1 - asp.orb / 10);

        return { ...asp, p1, p2, color, opacity, key: i };
      });
  }, [chartData, planetPositions]);

  const activePlanet = selectedPlanet || hoveredPlanet;
  const activeInfo = activePlanet && chartData?.planets?.[activePlanet];

  return (
    <div className="chart-wheel-container" style={{ position: 'relative' }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{
          background: 'radial-gradient(circle, #1a1a2e 0%, #0f0f1a 100%)',
          borderRadius: '50%',
        }}
      >
        {/* Background circles */}
        <circle cx={cx} cy={cy} r={outerRadius} fill="none" stroke="#333" strokeWidth="1" />
        <circle cx={cx} cy={cy} r={innerRadius} fill="none" stroke="#444" strokeWidth="1" />
        <circle cx={cx} cy={cy} r={houseRadius} fill="none" stroke="#333" strokeWidth="0.5" />
        <circle cx={cx} cy={cy} r={aspectRadius} fill="none" stroke="#222" strokeWidth="0.5" />

        {/* Zodiac segments */}
        {zodiacSegments.map(({ sign, d, symbolPos }) => (
          <g key={sign.name}>
            <path d={d} fill={sign.color} fillOpacity={0.15} stroke={sign.color} strokeWidth="1" />
            <text
              x={symbolPos.x}
              y={symbolPos.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill={sign.color}
              fontSize="18"
              fontFamily="serif"
            >
              {sign.symbol}
            </text>
          </g>
        ))}

        {/* House lines */}
        {houseLines.map(({ houseNum, inner, outer, labelPos }) => (
          <g key={houseNum}>
            <line
              x1={inner.x}
              y1={inner.y}
              x2={outer.x}
              y2={outer.y}
              stroke="#555"
              strokeWidth="1"
            />
            <text
              x={labelPos.x}
              y={labelPos.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#666"
              fontSize="10"
            >
              {houseNum}
            </text>
          </g>
        ))}

        {/* Aspect lines */}
        {aspectLines.map(({ p1, p2, color, opacity, key, aspect }) => (
          <motion.line
            key={key}
            x1={p1.x}
            y1={p1.y}
            x2={p2.x}
            y2={p2.y}
            stroke={color}
            strokeWidth={aspect === 'conjunction' ? 2 : 1}
            strokeOpacity={opacity}
            strokeDasharray={aspect === 'square' ? '4,2' : aspect === 'opposition' ? '8,4' : 'none'}
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1, delay: key * 0.05 }}
          />
        ))}

        {/* Planets */}
        {Object.entries(planetPositions).map(([name, pos]) => {
          const planet = PLANET_SYMBOLS[name] || { symbol: '?', color: '#888' };
          const isActive = activePlanet === name;

          return (
            <g
              key={name}
              style={{ cursor: interactive ? 'pointer' : 'default' }}
              onMouseEnter={() => interactive && setHoveredPlanet(name)}
              onMouseLeave={() => interactive && setHoveredPlanet(null)}
              onClick={() =>
                interactive && setSelectedPlanet(selectedPlanet === name ? null : name)
              }
            >
              <motion.circle
                cx={pos.x}
                cy={pos.y}
                r={isActive ? 18 : 14}
                fill="#1a1a2e"
                stroke={planet.color}
                strokeWidth={isActive ? 3 : 2}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200 }}
              />
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={planet.color}
                fontSize={isActive ? 16 : 14}
                fontFamily="serif"
              >
                {planet.symbol}
              </text>
            </g>
          );
        })}

        {/* Ascendant marker */}
        {chartData?.ascendant && (
          <g>
            <text
              x={
                polarToCartesian(
                  cx,
                  cy,
                  innerRadius + 5,
                  degreeToAngle(chartData.ascendant.sign, chartData.ascendant.degree)
                ).x
              }
              y={
                polarToCartesian(
                  cx,
                  cy,
                  innerRadius + 5,
                  degreeToAngle(chartData.ascendant.sign, chartData.ascendant.degree)
                ).y
              }
              fill="#4ecdc4"
              fontSize="12"
              fontWeight="bold"
            >
              ASC
            </text>
          </g>
        )}
      </svg>

      {/* Info panel */}
      {interactive && activeInfo && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            position: 'absolute',
            bottom: 10,
            left: '50%',
            transform: 'translateX(-50%)',
            background: 'rgba(0,0,0,0.85)',
            padding: '12px 20px',
            borderRadius: '8px',
            border: `1px solid ${PLANET_SYMBOLS[activePlanet]?.color || '#888'}`,
            color: '#fff',
            textAlign: 'center',
            minWidth: 200,
          }}
        >
          <div style={{ fontSize: 18, marginBottom: 4 }}>
            {PLANET_SYMBOLS[activePlanet]?.symbol} {activePlanet}
          </div>
          <div style={{ fontSize: 14, color: '#aaa' }}>
            {activeInfo.sign} {activeInfo.degree.toFixed(1)}° • House {activeInfo.house}
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default ChartWheel;

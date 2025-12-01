import { jsPDF } from 'jspdf';
import type { PredictionData } from '../types';

// Color palette for PDF
const COLORS = {
  primary: [136, 192, 208] as [number, number, number],
  accent: [191, 97, 106] as [number, number, number],
  dark: [11, 12, 21] as [number, number, number],
  text: [236, 239, 244] as [number, number, number],
  muted: [129, 161, 193] as [number, number, number],
};

// Section icons (for text representation)
const SECTION_ICONS: Record<string, string> = {
  'Love & Relationships': '❤️',
  'Career & Finance': '💼',
  'Health & Wellness': '🌿',
  'Personal Growth': '✨',
  'Overview': '🌟',
  'Daily Focus': '🎯',
  'Weekly Outlook': '📅',
  'Monthly Theme': '🌙',
};

/**
 * Generate and download a premium PDF reading.
 * All processing happens client-side in memory for privacy.
 */
export function downloadReadingPdf(data: PredictionData): void {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  const contentWidth = pageWidth - margin * 2;
  let y = 20;
  let currentPage = 1;

  // Helper to add a new page if needed
  const checkPageBreak = (neededSpace: number) => {
    if (y + neededSpace > pageHeight - 30) {
      addFooter();
      doc.addPage();
      currentPage++;
      y = 25;
      addPageHeader();
    }
  };

  // Helper to add page header on continuation pages
  const addPageHeader = () => {
    doc.setFontSize(10);
    doc.setTextColor(...COLORS.muted);
    doc.text('Astromeric Premium Reading', margin, 15);
    doc.setDrawColor(...COLORS.primary);
    doc.line(margin, 18, pageWidth - margin, 18);
    y = 30;
  };

  // Helper to add footer
  const addFooter = () => {
    doc.setFontSize(8);
    doc.setTextColor(128, 128, 128);
    doc.text(`Page ${currentPage}`, margin, pageHeight - 10);
    doc.text('Astromeric • Cosmic Wisdom', pageWidth / 2, pageHeight - 10, { align: 'center' });
    doc.text(new Date().toLocaleDateString(), pageWidth - margin, pageHeight - 10, { align: 'right' });
  };

  // Helper to add text with word wrap
  const addText = (text: string, fontSize: number, options: {
    isBold?: boolean;
    color?: [number, number, number];
    maxWidth?: number;
    align?: 'left' | 'center' | 'right';
    italic?: boolean;
  } = {}) => {
    const { isBold = false, color = COLORS.text, maxWidth = contentWidth, align = 'left', italic = false } = options;
    
    doc.setFontSize(fontSize);
    doc.setFont('helvetica', isBold ? 'bold' : italic ? 'italic' : 'normal');
    doc.setTextColor(...color);
    
    const lines = doc.splitTextToSize(text, maxWidth);
    checkPageBreak(lines.length * fontSize * 0.5 + 5);
    
    const xPos = align === 'center' ? pageWidth / 2 : align === 'right' ? pageWidth - margin : margin;
    doc.text(lines, xPos, y, { align });
    y += lines.length * fontSize * 0.45 + 5;
  };

  // Helper to add a styled section header
  const addSectionHeader = (title: string) => {
    checkPageBreak(25);
    
    const icon = SECTION_ICONS[title] || '★';
    
    // Draw decorative line
    doc.setDrawColor(...COLORS.primary);
    doc.setLineWidth(0.5);
    doc.line(margin, y, margin + 30, y);
    
    y += 8;
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.primary);
    doc.text(`${icon} ${title}`, margin, y);
    y += 10;
  };

  // Helper to add a bullet point
  const addBullet = (text: string, indent = 0) => {
    const bulletX = margin + indent;
    const textX = bulletX + 8;
    const maxWidth = contentWidth - indent - 8;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...COLORS.text);
    
    const lines = doc.splitTextToSize(text, maxWidth);
    checkPageBreak(lines.length * 5 + 3);
    
    // Draw bullet
    doc.setFillColor(...COLORS.primary);
    doc.circle(bulletX + 2, y - 2, 1.5, 'F');
    
    doc.text(lines, textX, y);
    y += lines.length * 5 + 3;
  };

  // Helper to add a quote box
  const addQuoteBox = (text: string, label?: string) => {
    const boxHeight = 25;
    checkPageBreak(boxHeight + 10);
    
    // Draw background
    doc.setFillColor(30, 35, 50);
    doc.roundedRect(margin, y - 3, contentWidth, boxHeight, 3, 3, 'F');
    
    // Draw left accent bar
    doc.setFillColor(...COLORS.accent);
    doc.rect(margin, y - 3, 3, boxHeight, 'F');
    
    if (label) {
      doc.setFontSize(8);
      doc.setTextColor(...COLORS.muted);
      doc.text(label, margin + 8, y + 3);
      y += 6;
    }
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'italic');
    doc.setTextColor(...COLORS.text);
    const lines = doc.splitTextToSize(text, contentWidth - 16);
    doc.text(lines, margin + 8, y + 3);
    y += boxHeight + 5;
  };

  // Helper to add a stat card
  const addStatCard = (label: string, value: string, x: number, width: number) => {
    doc.setFillColor(25, 30, 45);
    doc.roundedRect(x, y, width, 35, 3, 3, 'F');
    
    doc.setFontSize(9);
    doc.setTextColor(...COLORS.muted);
    doc.text(label, x + width / 2, y + 10, { align: 'center' });
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.primary);
    doc.text(value, x + width / 2, y + 25, { align: 'center' });
  };

  // === START BUILDING PDF ===

  // Title Page / Header
  doc.setFillColor(...COLORS.dark);
  doc.rect(0, 0, pageWidth, 60, 'F');
  
  doc.setFontSize(28);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(...COLORS.primary);
  doc.text('ASTROMERIC', pageWidth / 2, 25, { align: 'center' });
  
  doc.setFontSize(14);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(...COLORS.text);
  doc.text('Premium Cosmic Reading', pageWidth / 2, 38, { align: 'center' });
  
  const sunSign = data.sign || data.charts?.natal?.planets?.find((p) => p.name === 'Sun')?.sign;
  const moonSign = data.charts?.natal?.planets?.find((p) => p.name === 'Moon')?.sign;
  const lifePath = data.numerology?.core_numbers?.life_path?.number;
  
  doc.setFontSize(11);
  doc.setTextColor(...COLORS.muted);
  const profileText = [sunSign, moonSign ? `Moon in ${moonSign}` : null, lifePath ? `Life Path ${lifePath}` : null]
    .filter(Boolean)
    .join(' • ');
  if (profileText) {
    doc.text(profileText, pageWidth / 2, 50, { align: 'center' });
  }
  
  y = 75;

  // Stat Cards Row
  const cardWidth = (contentWidth - 20) / 3;
  addStatCard('Scope', data.scope.toUpperCase(), margin, cardWidth);
  addStatCard('Date', new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }), margin + cardWidth + 10, cardWidth);
  addStatCard('Sign', sunSign || '—', margin + (cardWidth + 10) * 2, cardWidth);
  y += 45;

  // Summary / TL;DR
  const headline = data.summary?.headline || data.theme;
  if (headline) {
    addQuoteBox(headline, '✨ TODAY\'S MESSAGE');
  }

  // Main Sections
  if (data.sections && data.sections.length > 0) {
    for (const section of data.sections) {
      addSectionHeader(section.title);
      
      if (section.highlights && section.highlights.length > 0) {
        for (const highlight of section.highlights) {
          addBullet(highlight);
        }
      }
      
      // Add affirmation if available
      if (section.affirmation) {
        y += 5;
        addQuoteBox(section.affirmation, '💫 AFFIRMATION');
      }
      
      y += 5;
    }
  }

  // Numerology Section
  if (data.numerology?.core_numbers) {
    checkPageBreak(80);
    
    y += 10;
    doc.setDrawColor(...COLORS.accent);
    doc.line(margin, y, pageWidth - margin, y);
    y += 15;
    
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.accent);
    doc.text('🔢 Numerology Profile', margin, y);
    y += 15;
    
    const core = data.numerology.core_numbers;
    
    // Life Path (most important)
    if (core.life_path) {
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.primary);
      doc.text(`Life Path ${core.life_path.number}`, margin, y);
      y += 8;
      
      if (core.life_path.meaning) {
        addText(core.life_path.meaning, 10, { color: COLORS.text });
      }
      y += 5;
    }

    // Other core numbers in columns
    const colWidth = contentWidth / 2 - 5;
    let leftY = y;
    let rightY = y;

    if (core.expression) {
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.text);
      doc.text(`Expression ${core.expression.number}`, margin, leftY);
      leftY += 6;
      
      if (core.expression.meaning) {
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        const lines = doc.splitTextToSize(core.expression.meaning, colWidth);
        doc.text(lines, margin, leftY);
        leftY += lines.length * 4 + 5;
      }
    }

    if (core.soul_urge) {
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.text);
      doc.text(`Soul Urge ${core.soul_urge.number}`, margin + colWidth + 10, rightY);
      rightY += 6;
      
      if (core.soul_urge.meaning) {
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        const lines = doc.splitTextToSize(core.soul_urge.meaning, colWidth);
        doc.text(lines, margin + colWidth + 10, rightY);
        rightY += lines.length * 4 + 5;
      }
    }

    y = Math.max(leftY, rightY) + 10;
  }

  // Current Cycles
  if (data.numerology?.cycles) {
    checkPageBreak(60);
    
    doc.setFontSize(13);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.primary);
    doc.text('📅 Current Cycles', margin, y);
    y += 12;
    
    const cycles = data.numerology.cycles;
    const cycleData = [
      { label: 'Personal Year', data: cycles.personal_year },
      { label: 'Personal Month', data: cycles.personal_month },
      { label: 'Personal Day', data: cycles.personal_day },
    ];

    for (const cycle of cycleData) {
      if (cycle.data) {
        doc.setFontSize(10);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...COLORS.text);
        doc.text(`${cycle.label} ${cycle.data.number}`, margin, y);
        y += 5;
        
        if (cycle.data.meaning) {
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(9);
          doc.setTextColor(...COLORS.muted);
          const lines = doc.splitTextToSize(cycle.data.meaning, contentWidth);
          checkPageBreak(lines.length * 4 + 8);
          doc.text(lines, margin, y);
          y += lines.length * 4 + 5;
        }
      }
    }
  }

  // Charts Data (if available)
  if (data.charts?.natal?.planets && data.charts.natal.planets.length > 0) {
    checkPageBreak(80);
    
    y += 10;
    doc.setDrawColor(...COLORS.primary);
    doc.line(margin, y, pageWidth - margin, y);
    y += 15;
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.primary);
    doc.text('🌟 Planetary Positions', margin, y);
    y += 12;

    // Table header
    doc.setFillColor(25, 30, 45);
    doc.rect(margin, y, contentWidth, 8, 'F');
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.muted);
    doc.text('Planet', margin + 5, y + 5.5);
    doc.text('Sign', margin + 45, y + 5.5);
    doc.text('Degree', margin + 90, y + 5.5);
    doc.text('House', margin + 130, y + 5.5);
    y += 10;

    // Table rows
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...COLORS.text);
    
    for (const planet of data.charts.natal.planets.slice(0, 10)) {
      checkPageBreak(8);
      
      doc.setFontSize(9);
      doc.text(planet.name, margin + 5, y + 4);
      doc.text(planet.sign, margin + 45, y + 4);
      doc.text(`${planet.degree.toFixed(1)}°`, margin + 90, y + 4);
      doc.text(`${planet.house}`, margin + 130, y + 4);
      
      doc.setDrawColor(40, 45, 60);
      doc.line(margin, y + 7, pageWidth - margin, y + 7);
      y += 9;
    }
  }

  // Disclaimer
  y = Math.min(y + 15, pageHeight - 45);
  doc.setFillColor(25, 30, 45);
  doc.roundedRect(margin, y, contentWidth, 25, 3, 3, 'F');
  doc.setFontSize(8);
  doc.setFont('helvetica', 'italic');
  doc.setTextColor(...COLORS.muted);
  const disclaimer = 'This reading is for entertainment and self-reflection purposes. The insights provided are based on astrological and numerological traditions and should not replace professional advice.';
  const disclaimerLines = doc.splitTextToSize(disclaimer, contentWidth - 10);
  doc.text(disclaimerLines, margin + 5, y + 8);

  // Final Footer
  addFooter();

  // Download
  const fileName = `astromeric-premium-${data.scope}-${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
}

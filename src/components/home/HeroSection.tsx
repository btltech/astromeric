import React from 'react';
import { Link } from 'react-router-dom';
import { InsightPreviewCard, type InsightPreview } from './InsightPreviewCard';

type HeroSectionProps = {
  title: string;
  description: string;
  primaryLabel: string;
  primaryTo: string;
  secondaryLabel: string;
  secondaryHref: string;
  insight: InsightPreview;
};

export function HeroSection({
  title,
  description,
  primaryLabel,
  primaryTo,
  secondaryLabel,
  secondaryHref,
  insight,
}: HeroSectionProps) {
  return (
    <section className="hero-section">
      <div className="hero-section__grid">
        <div className="hero-section__copy home-premium__panel">
          <h1 className="hero-section__title">{title}</h1>
          <p className="hero-section__description">{description}</p>

          <div className="hero-section__actions">
            <Link className="home-button home-button--primary" to={primaryTo}>
              {primaryLabel}
            </Link>
            <a className="home-button home-button--secondary" href={secondaryHref}>
              {secondaryLabel}
            </a>
          </div>
        </div>

        <InsightPreviewCard compact {...insight} />
      </div>

      <nav className="hero-section__jump-links" aria-label="Homepage sections">
        <a className="hero-section__jump-link" href="#how-it-works">How it works</a>
        <a className="hero-section__jump-link" href="#what-you-get">What you get</a>
      </nav>
    </section>
  );
}

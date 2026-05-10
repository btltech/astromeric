import React from 'react';
import { Link } from 'react-router-dom';

type CTASectionProps = {
  eyebrow: string;
  title: string;
  description: string;
  primaryLabel: string;
  primaryTo: string;
  secondaryLabel: string;
  secondaryTo: string;
};

export function CTASection({
  eyebrow,
  title,
  description,
  primaryLabel,
  primaryTo,
  secondaryLabel,
  secondaryTo,
}: CTASectionProps) {
  return (
    <section className="cta-section home-premium__panel">
      <div className="cta-section__copy">
        <span className="cta-section__eyebrow">{eyebrow}</span>
        <h2 className="cta-section__title">{title}</h2>
        <p className="cta-section__description">{description}</p>
      </div>

      <div className="cta-section__actions">
        <Link className="home-button home-button--primary" to={primaryTo}>
          {primaryLabel}
        </Link>
        <Link className="home-button home-button--secondary" to={secondaryTo}>
          {secondaryLabel}
        </Link>
      </div>
    </section>
  );
}

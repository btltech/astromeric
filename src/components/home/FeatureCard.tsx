import React from 'react';
import { Link } from 'react-router-dom';

type FeatureCardProps = {
  eyebrow: string;
  title: string;
  description: string;
  value?: string;
  href?: string;
  linkLabel?: string;
  highlight?: boolean;
};

export function FeatureCard({
  eyebrow,
  title,
  description,
  value,
  href,
  linkLabel,
  highlight = false,
}: FeatureCardProps) {
  return (
    <article className={`feature-card${highlight ? ' feature-card--highlight' : ''}`}>
      <span className="feature-card__eyebrow">{eyebrow}</span>
      {value ? <div className="feature-card__value">{value}</div> : null}
      <h3 className="feature-card__title">{title}</h3>
      <p className="feature-card__description">{description}</p>
      {href && linkLabel ? (
        <Link className="feature-card__link" to={href}>
          {linkLabel}
        </Link>
      ) : null}
    </article>
  );
}

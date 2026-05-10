import React from 'react';
import { DocumentMeta } from '../components/DocumentMeta';
import { CTASection } from '../components/home/CTASection';
import { FeatureCard } from '../components/home/FeatureCard';
import { HeroSection } from '../components/home/HeroSection';
import { type InsightPreview } from '../components/home/InsightPreviewCard';
import './HomeSupportView.css';

const heroInsight: InsightPreview = {
  label: "Today's signal",
  headline: 'Calm focus with one strong window for decisions and outreach.',
  score: '82',
  scoreLabel: 'Strong',
  mood: 'Clear and steady',
  bestTime: '8:40 AM \u2013 10:10 AM',
  nextAction: 'Start with the conversation or decision you have been delaying.',
  chartInfluence: 'Moon focus',
  numerologyCycle: 'Year 6',
};

const productFeatures = [
  {
    eyebrow: 'Daily insight',
    title: 'A clear signal every morning',
    description: 'See your score, mood, best window, and next move — all in one view before the day starts.',
    href: '/reading',
    linkLabel: 'See a preview',
  },
  {
    eyebrow: 'Birth chart',
    title: 'Read your chart without the noise',
    description: 'Placements, aspects, and patterns in a structured view that is easy to scan and navigate.',
    href: '/charts',
    linkLabel: 'See a preview',
  },
  {
    eyebrow: 'Numerology',
    title: 'Year, month, and day cycles in one place',
    description: 'Your Life Path, personal year, and daily number — visible and connected, not scattered.',
    href: '/numerology',
    linkLabel: 'See a preview',
  },
  {
    eyebrow: 'Timing',
    title: 'Know the best windows before you decide',
    description: 'Check timing before a call, a launch, or a difficult conversation. Plain language, no jargon.',
    href: '/tools',
    linkLabel: 'See a preview',
  },
] as const;

const howItWorksSteps = [
  {
    step: '1',
    title: 'Create your profile',
    description: 'Add your birth date, time, and location. Takes two minutes, done once.',
  },
  {
    step: '2',
    title: "Read today's signal",
    description: 'Score, mood, best window, and next action — in one clear view each morning.',
  },
  {
    step: '3',
    title: 'Go deeper when you want',
    description: 'Open your birth chart, numbers, compatibility, and timing from the same profile.',
  },
] as const;

export function HomeSupportView() {
  return (
    <>
      <DocumentMeta
        title="AstroNumeric | Daily Insight, Birth Chart & Numerology"
        description="AstroNumeric combines astrology, numerology, compatibility, and timing guidance in one calm personal insight experience."
      />

      <div className="home-premium">
        <HeroSection
          title="Your birth chart, core numbers, and daily timing — in one clear view."
          description="AstroNumeric turns three systems into a single daily signal you can read and act on in seconds."
          primaryLabel="Start Your Free Reading"
          primaryTo="/reading"
          secondaryLabel="See How It Works"
          secondaryHref="#how-it-works"
          insight={heroInsight}
        />

        <section id="how-it-works" className="home-premium__section">
          <div className="home-premium__section-intro">
            <h2 className="home-premium__section-title">From profile to insight in under a minute.</h2>
            <p className="home-premium__section-desc">Three steps. No complicated setup.</p>
          </div>
          <div className="how-it-works__steps">
            {howItWorksSteps.map((step) => (
              <div key={step.step} className="how-it-works__step">
                <span className="how-it-works__badge">{step.step}</span>
                <h3 className="how-it-works__step-title">{step.title}</h3>
                <p className="how-it-works__step-description">{step.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="what-you-get" className="home-premium__section">
          <div className="home-premium__section-intro">
            <h2 className="home-premium__section-title">Everything you need, nothing you don't.</h2>
            <p className="home-premium__section-desc">Start with a daily signal, go deeper when you want more context.</p>
          </div>

          <div className="home-premium__feature-grid home-premium__feature-grid--four">
            {productFeatures.map((feature) => (
              <FeatureCard
                key={feature.title}
                eyebrow={feature.eyebrow}
                title={feature.title}
                description={feature.description}
                href={feature.href}
                linkLabel={feature.linkLabel}
              />
            ))}
          </div>
        </section>

        <CTASection
          eyebrow="Ready when you are"
          title="Your signal is waiting. It takes two minutes to set up."
          description="One profile unlocks your daily reading, birth chart, numerology cycles, and compatibility — all connected."
          primaryLabel="Start Your Free Reading"
          primaryTo="/reading"
          secondaryLabel="Open Birth Chart"
          secondaryTo="/charts"
        />
      </div>
    </>
  );
}

export default HomeSupportView;

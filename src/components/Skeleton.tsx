import React from 'react';

interface SkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  className?: string;
  count?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  className = '',
  count = 1,
}) => {
  const getStyles = (): React.CSSProperties => {
    const baseStyles: React.CSSProperties = {
      background: 'linear-gradient(90deg, rgba(139, 92, 246, 0.1) 25%, rgba(139, 92, 246, 0.2) 50%, rgba(139, 92, 246, 0.1) 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 1.5s infinite',
      borderRadius: variant === 'circular' ? '50%' : variant === 'card' ? '1rem' : '0.25rem',
    };

    if (width) baseStyles.width = typeof width === 'number' ? `${width}px` : width;
    if (height) baseStyles.height = typeof height === 'number' ? `${height}px` : height;

    if (variant === 'text' && !height) baseStyles.height = '1rem';
    if (variant === 'circular' && !width) {
      baseStyles.width = '40px';
      baseStyles.height = '40px';
    }
    if (variant === 'card' && !height) baseStyles.height = '200px';

    return baseStyles;
  };

  const items = Array.from({ length: count }, (_, i) => (
    <div key={i} className={`skeleton ${className}`} style={getStyles()} />
  ));

  return (
    <>
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
        .skeleton {
          display: block;
        }
        .skeleton + .skeleton {
          margin-top: 0.5rem;
        }
      `}</style>
      {items}
    </>
  );
};

// Pre-built skeleton components for common use cases
export const CardSkeleton: React.FC = () => (
  <div className="card-skeleton" style={{
    background: 'rgba(139, 92, 246, 0.05)',
    borderRadius: '1rem',
    padding: '1.5rem',
    border: '1px solid rgba(139, 92, 246, 0.1)',
  }}>
    <Skeleton variant="text" width="60%" height={24} />
    <div style={{ marginTop: '1rem' }}>
      <Skeleton variant="text" count={3} />
    </div>
    <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
      <Skeleton variant="rectangular" width={80} height={32} />
      <Skeleton variant="rectangular" width={80} height={32} />
    </div>
  </div>
);

export const ProfileSkeleton: React.FC = () => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
    <Skeleton variant="circular" width={64} height={64} />
    <div style={{ flex: 1 }}>
      <Skeleton variant="text" width="40%" height={20} />
      <Skeleton variant="text" width="60%" height={16} />
    </div>
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div style={{ textAlign: 'center', padding: '2rem' }}>
    <Skeleton variant="circular" width={300} height={300} className="mx-auto" />
    <div style={{ marginTop: '1.5rem' }}>
      <Skeleton variant="text" width="50%" height={24} />
      <Skeleton variant="text" count={2} />
    </div>
  </div>
);

export const ReadingSkeleton: React.FC = () => (
  <div className="skeleton-card">
    <div className="skeleton-heading" />
    <div className="skeleton-line short" />
    <div className="skeleton-line medium" />
    <div className="skeleton-line" />
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1.5rem' }}>
      <div>
        <div className="skeleton-line short" />
        <div className="skeleton-line" />
      </div>
      <div>
        <div className="skeleton-line short" />
        <div className="skeleton-line" />
      </div>
    </div>
  </div>
);

export const FormSkeleton: React.FC = () => (
  <div className="skeleton-card">
    <div className="skeleton-heading" style={{ width: '40%' }} />
    <div className="skeleton-line" style={{ height: '2.5rem', marginBottom: '1rem' }} />
    <div className="skeleton-line" style={{ height: '2.5rem', marginBottom: '1rem' }} />
    <div className="skeleton-line" style={{ height: '2.5rem', marginBottom: '1rem' }} />
    <div className="skeleton-line" style={{ height: '3rem', width: '50%', marginTop: '1.5rem' }} />
  </div>
);

export default Skeleton;

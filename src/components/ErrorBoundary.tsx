import React from 'react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-content">
            <h2>Something went wrong in the cosmos...</h2>
            <p>We encountered an unexpected error. Please try refreshing the page.</p>
            <button className="btn-primary" onClick={() => window.location.reload()}>
              Refresh Page
            </button>
            {process.env.NODE_ENV === 'development' && (
              <details>
                <summary>Error Details</summary>
                <pre>{this.state.error?.toString()}</pre>
              </details>
            )}
          </div>
          <style>{`
            .error-boundary {
              display: flex;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              background: #0f172a;
              color: #e2e8f0;
              text-align: center;
              padding: 2rem;
            }
            .error-content {
              background: rgba(30, 41, 59, 0.8);
              padding: 2rem;
              border-radius: 1rem;
              border: 1px solid rgba(148, 163, 184, 0.1);
              max-width: 500px;
            }
            h2 { margin-bottom: 1rem; color: #a78bfa; }
            p { margin-bottom: 1.5rem; }
            .btn-primary {
              background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
              color: white;
              border: none;
              padding: 0.75rem 1.5rem;
              border-radius: 0.5rem;
              cursor: pointer;
              font-weight: 600;
              transition: opacity 0.2s;
            }
            .btn-primary:hover { opacity: 0.9; }
            details { margin-top: 1.5rem; text-align: left; font-size: 0.875rem; }
            pre { 
              background: #000; 
              padding: 1rem; 
              border-radius: 0.5rem; 
              overflow-x: auto; 
              margin-top: 0.5rem;
            }
          `}</style>
        </div>
      );
    }

    return this.props.children;
  }
}

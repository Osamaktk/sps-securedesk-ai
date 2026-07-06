import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary] Caught render error:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo?.componentStack);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            display: 'flex',
            minHeight: '100vh',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
            background: '#f7f9fc',
            color: '#111827',
            fontFamily: 'Inter, "Segoe UI", Arial, sans-serif',
          }}
        >
          <div
            style={{
              maxWidth: '480px',
              padding: '32px',
              border: '1px solid #e5e7eb',
              borderRadius: '14px',
              background: '#ffffff',
              boxShadow: '0 10px 30px rgba(11, 31, 77, 0.08)',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                display: 'grid',
                width: '54px',
                height: '54px',
                margin: '0 auto 18px',
                placeItems: 'center',
                border: '1px solid #f0c8cc',
                borderRadius: '13px',
                background: '#fff0f1',
                color: '#a62b34',
                fontSize: '20px',
                fontWeight: 850,
              }}
              aria-hidden="true"
            >
              !
            </div>
            <h1
              style={{
                margin: 0,
                fontSize: '18px',
                fontWeight: 750,
                color: '#0b1f4d',
              }}
            >
              Something went wrong
            </h1>
            <p
              style={{
                margin: '10px 0 0',
                fontSize: '13px',
                lineHeight: 1.65,
                color: '#6b7280',
              }}
            >
              SecureDesk AI encountered an unexpected error.
              <br />
              Please try refreshing the page.
            </p>
            <p
              style={{
                margin: '14px 0 0',
                fontSize: '10px',
                color: '#9ca3af',
                wordBreak: 'break-word',
              }}
            >
              {this.state.error?.message || 'Unknown error'}
            </p>
            {(this.state.error?.stack || this.state.errorInfo?.componentStack) && (
              <pre
                style={{
                  maxHeight: '180px',
                  overflow: 'auto',
                  margin: '14px 0 0',
                  padding: '10px',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  background: '#f9fafb',
                  color: '#4b5563',
                  fontSize: '10px',
                  lineHeight: 1.5,
                  textAlign: 'left',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {this.state.error?.stack || this.state.errorInfo?.componentStack}
              </pre>
            )}
            <button
              type="button"
              onClick={() => window.location.reload()}
              style={{
                marginTop: '22px',
                padding: '10px 22px',
                border: '1px solid #005bbb',
                borderRadius: '8px',
                background: '#005bbb',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 750,
                boxShadow: '0 8px 18px rgba(0, 91, 187, 0.2)',
              }}
            >
              Refresh page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

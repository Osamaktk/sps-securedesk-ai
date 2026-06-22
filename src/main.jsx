import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import './styles/global.css';
import './styles/sps-theme.css';
import './styles/responsive.css';

const rootElement = document.getElementById('root');

function renderBootstrapError(error) {
  const container = rootElement || document.body.appendChild(document.createElement('div'));
  container.replaceChildren();

  const wrapper = document.createElement('main');
  wrapper.setAttribute('role', 'alert');
  wrapper.style.cssText = [
    'min-height:100vh',
    'display:grid',
    'place-items:center',
    'padding:24px',
    'font-family:Inter, Segoe UI, Arial, sans-serif',
    'background:#f7f9fc',
    'color:#111827',
  ].join(';');

  const panel = document.createElement('section');
  panel.style.cssText = [
    'width:min(620px, 100%)',
    'padding:28px',
    'border:1px solid #e5e7eb',
    'border-radius:12px',
    'background:#fff',
    'box-shadow:0 10px 30px rgba(11,31,77,.08)',
  ].join(';');

  const title = document.createElement('h1');
  title.textContent = 'SecureDesk AI could not start';
  title.style.cssText = 'margin:0 0 10px;color:#0b1f4d;font-size:20px';

  const message = document.createElement('pre');
  message.textContent = error?.stack || error?.message || String(error);
  message.style.cssText = [
    'margin:0',
    'white-space:pre-wrap',
    'word-break:break-word',
    'font-size:12px',
    'line-height:1.6',
    'color:#6b7280',
  ].join(';');

  panel.append(title, message);
  wrapper.append(panel);
  container.append(wrapper);
}

window.addEventListener('error', (event) => {
  console.error('[global error]', event.error || event.message);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('[unhandled rejection]', event.reason);
});

try {
  if (!rootElement) {
    throw new Error('Root element #root was not found.');
  }

  ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>,
  );
} catch (error) {
  console.error('[main] Failed to mount React app:', error);
  renderBootstrapError(error);
}

import { Link } from 'react-router-dom';
import { useState } from 'react';
import api from '../../services/api';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      await api.post('/auth/forgot-password', { email });
      setSubmitted(true);
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-panel">
        <div className="login-panel__intro">
          <h1>Forgot Password</h1>
          <p>Enter your registered email to receive a password reset link.</p>
        </div>

        {!submitted ? (
          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              Registered email
              <input
                type="email"
                placeholder="name@company.com"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        ) : (
          <div className="login-form" style={{ textAlign: 'center' }}>
            <p style={{ color: '#16a34a', fontWeight: 600 }}>
              If an account exists for {email}, a reset link has been sent. Check your inbox.
            </p>
          </div>
        )}

        <p className="login-panel__note">
          <Link to="/login">Back to Sign In</Link>
        </p>
      </section>
      <aside className="login-visual">
        <div className="login-visual__content">
          <span className="login-visual__label">SPS SecureDesk AI</span>
          <h2>Reset your password securely.</h2>
          <p>We'll send a reset link to your registered email address.</p>
        </div>
      </aside>
    </main>
  );
}

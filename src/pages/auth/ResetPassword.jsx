import { Link, useSearchParams } from 'react-router-dom';
import { useState, useMemo } from 'react';
import api from '../../services/api';

function getPasswordStrength(password) {
  if (!password) return { label: '', level: 0, color: '#e2e8f0' };
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[!@#$%^&*()_+\-=[\]{}|;':",./<>?]/.test(password)) score++;
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score++;

  if (score <= 1) return { label: 'Weak', level: 1, color: '#ef4444' };
  if (score <= 2) return { label: 'Fair', level: 2, color: '#f59e0b' };
  if (score <= 3) return { label: 'Good', level: 3, color: '#3b82f6' };
  return { label: 'Strong', level: 4, color: '#16a34a' };
}

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const strength = useMemo(() => getPasswordStrength(password), [password]);

  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=[\]{}|;':",./<>?]/.test(password);
  const hasMinLength = password.length >= 8;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.post('/auth/reset-password', { token, password });
      setSuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join('. '));
      } else {
        setError(detail || 'Failed to reset password. The link may have expired.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!token) {
    return (
      <main className="login-page">
        <section className="login-panel">
          <div className="login-panel__intro">
            <h1>Invalid Link</h1>
            <p>This password reset link is invalid or has expired.</p>
          </div>
          <p className="login-panel__note">
            <Link to="/forgot-password">Request a new reset link</Link>
          </p>
        </section>
        <aside className="login-visual">
          <div className="login-visual__content">
            <span className="login-visual__label">SPS SecureDesk AI</span>
            <h2>Secure password reset.</h2>
          </div>
        </aside>
      </main>
    );
  }

  return (
    <main className="login-page">
      <section className="login-panel">
        <div className="login-panel__intro">
          <h1>Set New Password</h1>
          <p>Enter your new password below. It must be at least 8 characters with one number and one special character.</p>
        </div>

        {success ? (
          <div className="login-form" style={{ textAlign: 'center' }}>
            <p style={{ color: '#16a34a', fontWeight: 600, fontSize: '15px' }}>
              Password reset successfully!
            </p>
            <p className="login-panel__note" style={{ marginTop: '16px' }}>
              <Link to="/login">Go to Sign In</Link>
            </p>
          </div>
        ) : (
          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              New Password
              <input
                type="password"
                placeholder="Enter new password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>

            {password && (
              <div className="password-strength">
                <div className="password-strength__bar">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="password-strength__segment"
                      style={{
                        backgroundColor: i <= strength.level ? strength.color : '#e2e8f0',
                      }}
                    />
                  ))}
                </div>
                <span className="password-strength__label" style={{ color: strength.color }}>
                  {strength.label}
                </span>
              </div>
            )}

            {password && (
              <ul className="password-rules">
                <li className={hasMinLength ? 'valid' : ''}>
                  {hasMinLength ? '✓' : '○'} Minimum 8 characters
                </li>
                <li className={hasNumber ? 'valid' : ''}>
                  {hasNumber ? '✓' : '○'} At least one number
                </li>
                <li className={hasSpecial ? 'valid' : ''}>
                  {hasSpecial ? '✓' : '○'} At least one special character
                </li>
              </ul>
            )}

            <label>
              Confirm Password
              <input
                type="password"
                placeholder="Re-enter new password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </label>

            {error && <p className="form-error" role="alert">{error}</p>}

            <button
              className="primary-button"
              type="submit"
              disabled={isSubmitting || !hasMinLength || !hasNumber || !hasSpecial}
            >
              {isSubmitting ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        <p className="login-panel__note">
          <Link to="/login">Back to Sign In</Link>
        </p>
      </section>
      <aside className="login-visual">
        <div className="login-visual__content">
          <span className="login-visual__label">SPS SecureDesk AI</span>
          <h2>Secure password reset.</h2>
          <p>Your new password is encrypted and stored securely.</p>
        </div>
      </aside>
    </main>
  );
}

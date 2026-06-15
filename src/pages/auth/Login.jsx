import { Link } from 'react-router-dom';
import Brand from '../../components/common/Brand';

export default function Login() {
  return (
    <main className="login-page">
      <section className="login-panel">
        <Brand />
        <div className="login-panel__intro">
          <p className="eyebrow">Secure service operations</p>
          <h1>Sign in to SecureDesk AI</h1>
          <p>
            Access the enterprise helpdesk workspace for IT, security, cloud,
            and operational support.
          </p>
        </div>
        <form className="login-form">
          <label>
            Work email
            <input type="email" placeholder="name@company.com" disabled />
          </label>
          <label>
            Password
            <input type="password" placeholder="********" disabled />
          </label>
          <Link className="primary-button" to="/requester">
            Enter mock workspace
          </Link>
        </form>
        <p className="login-panel__note">
          Authentication is intentionally disabled in this frontend-only phase.
        </p>
      </section>
      <aside className="login-visual">
        <div className="login-visual__content">
          <span className="login-visual__label">SPS SecureDesk AI</span>
          <h2>One secure workspace for enterprise support operations.</h2>
          <p>
            A focused foundation for requester service, agent workflows,
            cybersecurity approvals, management reporting, and administration.
          </p>
        </div>
      </aside>
    </main>
  );
}

import { Link } from 'react-router-dom';
import Brand from '../components/common/Brand';
import HeroIll from '../assets/images/hero-illustration.svg';
import HeroTablet from '../assets/images/hero-illustration-tablet.svg';
import HeroMobile from '../assets/images/hero-illustration-mobile.svg';

export default function Home() {
  return (
    <main className="home-page">
      <header className="home-hero">
        <a className="skip-link" href="#main">Skip to content</a>
        <div className="home-hero__inner">
          <div className="home-header">
            <Brand />
            <nav className="home-nav">
              <Link to="/login">Sign in</Link>
              <Link to="/register" className="button button--outline">Get started</Link>
            </nav>
          </div>

          <div id="main" className="home-hero__content" role="main">
            <h1>Secure service operations for AI, Cloud & Security</h1>
            <p className="lead">A single workspace for IT, DevOps, identity & compliance — fast, reliable, and secure.</p>

            <div className="home-cta">
              <Link to="/register" className="primary-button">Get started</Link>
              <Link to="#features" className="secondary-button">Learn more</Link>
            </div>
          </div>
          <div className="home-hero__visual" aria-hidden="true">
            <picture>
              <source srcSet={HeroTablet} media="(min-width:640px) and (max-width:979px)" />
              <source srcSet={HeroIll} media="(min-width:980px)" />
              <img src={HeroMobile} alt="" loading="lazy" />
            </picture>
          </div>
        </div>
      </header>

      <section id="features" className="home-features">
        <div className="container">
          <h2>What we do</h2>
          <p className="home-features__intro">Integrated tools for AI, cloud, automation, cybersecurity, identity, DevOps, monitoring and compliance.</p>

          <div className="feature-grid">
            <article className="feature-card">
              <h3>AI-driven support</h3>
              <p>Automated classification, summarisation and suggested resolutions to speed ticket handling.</p>
            </article>
            <article className="feature-card">
              <h3>Cloud & DevOps</h3>
              <p>Streamlined workflows for cloud operations, incident response and automation.</p>
            </article>
            <article className="feature-card">
              <h3>Security & Identity</h3>
              <p>Integrated approvals, audit trails and identity-aware access controls.</p>
            </article>
            <article className="feature-card">
              <h3>Compliance & Reporting</h3>
              <p>Management dashboards, SLA monitoring and exportable compliance reports.</p>
            </article>
          </div>
        </div>
      </section>
    </main>
  );
}

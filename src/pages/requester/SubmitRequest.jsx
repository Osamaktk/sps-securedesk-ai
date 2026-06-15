import { useState } from 'react';
import { Link } from 'react-router-dom';
import Badge from '../../components/common/Badge';
import Card from '../../components/common/Card';
import RequestForm from '../../components/forms/RequestForm';
import { createTicketFromForm } from '../../services/ticketService.js';

export default function SubmitRequest() {
  const [confirmation, setConfirmation] = useState(null);

  const submitRequest = async (data) => {
    await createTicketFromForm(data);
    setConfirmation({
      id: 'SPS-2026-015',
      source: 'portal_form',
      status: 'New',
      email: data.requesterEmail,
    });
  };

  return (
    <section className="page submit-request-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Requester portal</p>
          <h1>Submit Request</h1>
          <p>
            Provide the details needed to route your request to the appropriate
            SPS support team.
          </p>
        </div>
        <Badge value="portal_form" />
      </div>

      {confirmation ? (
        <section className="request-confirmation" role="status">
          <span className="request-confirmation__icon" aria-hidden="true">
            OK
          </span>
          <div>
            <p className="eyebrow">Request submitted</p>
            <h2>Ticket SPS-2026-015 created successfully.</h2>
            <p>
              Your request is now available in the unified helpdesk ticket
              system.
            </p>
            <div className="request-confirmation__badges">
              <Badge value={confirmation.source} />
              <Badge tone="blue">{confirmation.status}</Badge>
            </div>
            <strong>
              Email confirmation will be sent to requester at {confirmation.email}.
            </strong>
            <div className="request-confirmation__actions">
              <Link className="button button--primary" to="/requester/tickets">
                View My Tickets
              </Link>
              <button
                className="button button--outline"
                type="button"
                onClick={() => setConfirmation(null)}
              >
                Submit another request
              </button>
            </div>
          </div>
        </section>
      ) : (
        <div className="submit-request-layout">
          <Card
            className="submit-request-form-card"
            title="Request details"
            subtitle="All fields use mock data and remain in the frontend session."
          >
            <RequestForm onSubmit={submitRequest} />
          </Card>

          <aside className="submit-request-guidance">
            <Card title="Before you submit" subtitle="Help us route the request quickly.">
              <ul className="request-guidance-list">
                <li>Describe the business impact and affected users.</li>
                <li>Include exact error messages and when the issue started.</li>
                <li>Attach screenshots or diagnostics without sensitive secrets.</li>
                <li>Use AI Chat first for common VPN, access, and onboarding questions.</li>
              </ul>
            </Card>
            <div className="request-security-note">
              <span aria-hidden="true">!</span>
              <p>Sensitive access and cybersecurity requests require human approval.</p>
            </div>
          </aside>
        </div>
      )}
    </section>
  );
}

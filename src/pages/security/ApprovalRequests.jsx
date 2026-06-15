import { useState } from 'react';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { mockTickets } from '../../data/mockTickets.js';

const approvalTicketIds = ['SPS-2026-002', 'SPS-2026-012'];

const riskReasons = {
  'SPS-2026-002':
    'Privileged analytics access can expose sensitive security telemetry and incident data.',
  'SPS-2026-012':
    'Service account certificate renewal affects a non-human identity and production authentication.',
};

export default function ApprovalRequests() {
  const approvals = mockTickets.filter((ticket) => approvalTicketIds.includes(ticket.id));
  const [decisions, setDecisions] = useState({});

  const setDecision = (ticketId, decision) => {
    setDecisions((current) => ({ ...current, [ticketId]: decision }));
  };

  return (
    <section className="page approval-requests-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Security operations</p>
          <h1>Approval Requests</h1>
          <p>Review high-risk identity and access requests requiring human authorization.</p>
        </div>
        <Badge tone="red">{approvals.length} sensitive requests</Badge>
      </div>

      <div className="human-approval-banner">
        <span aria-hidden="true">!</span>
        <div>
          <strong>AI never approves sensitive access. Human approval is required.</strong>
          <p>AI classification supports review but cannot authorize, reject, or provision access.</p>
        </div>
      </div>

      <div className="approval-card-list">
        {approvals.map((ticket) => {
          const decision = decisions[ticket.id];
          return (
            <article className="approval-card" key={ticket.id}>
              <div className="approval-card__header">
                <div>
                  <span>{ticket.id}</span>
                  <h2>{ticket.subject}</h2>
                </div>
                <Badge tone={decision ? 'blue' : 'amber'}>
                  {decision || 'Waiting Approval'}
                </Badge>
              </div>

              <dl className="approval-card__details">
                <div>
                  <dt>Requester</dt>
                  <dd>
                    <strong>{ticket.requesterName}</strong>
                    <span>{ticket.requesterEmail}</span>
                  </dd>
                </div>
                <div>
                  <dt>Requested access</dt>
                  <dd>{ticket.subject}</dd>
                </div>
                <div>
                  <dt>Risk reason</dt>
                  <dd>{riskReasons[ticket.id]}</dd>
                </div>
                <div>
                  <dt>AI classification note</dt>
                  <dd>{ticket.aiSummary}</dd>
                </div>
              </dl>

              <div className="approval-card__footer">
                <div className="approval-card__risk">
                  <Badge tone="red">{ticket.risk}</Badge>
                  <Badge value={ticket.source} />
                </div>
                <div className="approval-card__actions">
                  <Button variant="success" onClick={() => setDecision(ticket.id, 'Approved')}>
                    Approve
                  </Button>
                  <Button variant="danger" onClick={() => setDecision(ticket.id, 'Rejected')}>
                    Reject
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setDecision(ticket.id, 'More Info Requested')}
                  >
                    Request More Info
                  </Button>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

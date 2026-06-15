import { Link } from 'react-router-dom';
import Badge from '../../components/common/Badge';
import Card from '../../components/common/Card';
import StatCard from '../../components/common/StatCard';
import TicketPriorityBadge from '../../components/tickets/TicketPriorityBadge';
import TicketStatusBadge from '../../components/tickets/TicketStatusBadge';
import { mockTickets } from '../../data/mockTickets.js';

export default function SecurityDashboard() {
  const highRisk = mockTickets.filter((ticket) => ticket.risk === 'High Risk');
  const incidents = mockTickets.filter((ticket) => ticket.category === 'Cybersecurity');
  const approvals = mockTickets.filter((ticket) => ticket.status === 'Waiting Approval');
  const phishingReports = 2;

  return (
    <section className="page security-dashboard-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Security operations</p>
          <h1>Security Dashboard</h1>
          <p>Monitor high-risk tickets, incidents, phishing reports, and approval activity.</p>
        </div>
        <Badge tone="red">Human review active</Badge>
      </div>

      <div className="security-stat-grid">
        <StatCard title="High-risk queue" value={highRisk.length} icon="HR" trend="Review" trendDirection="warning" description="Security and access tickets" />
        <StatCard title="Security incidents" value={incidents.length} icon="SI" trend="Active" description="Cybersecurity category tickets" />
        <StatCard title="Phishing reports" value={phishingReports} icon="PH" trend="+1 today" trendDirection="warning" description="Mock suspected phishing reports" />
        <StatCard title="Waiting approval" value={approvals.length} icon="AP" trend="Human action" trendDirection="warning" description="Sensitive requests awaiting review" />
      </div>

      <div className="security-dashboard-grid">
        <Card
          className="security-queue-card"
          title="High-Risk Queue"
          subtitle="Tickets requiring security operations review."
          actions={
            <Link className="dashboard-text-link" to="/security/approvals">
              Review approvals
            </Link>
          }
        >
          <div className="security-ticket-list">
            {highRisk.map((ticket) => (
              <Link key={ticket.id} to={`/agent/tickets/${ticket.id}`}>
                <span className="security-ticket-list__icon" aria-hidden="true">!</span>
                <span className="security-ticket-list__content">
                  <strong>{ticket.subject}</strong>
                  <small>{ticket.id} - {ticket.requesterName}</small>
                </span>
                <span className="security-ticket-list__badges">
                  <TicketStatusBadge status={ticket.status} />
                  <TicketPriorityBadge priority={ticket.priority} />
                </span>
              </Link>
            ))}
          </div>
        </Card>

        <Card title="Approval Statistics" subtitle="Mock review outcomes for this month.">
          <div className="approval-stat-list">
            <div><span>Waiting Approval</span><strong>3</strong></div>
            <div><span>Approved</span><strong>14</strong></div>
            <div><span>Rejected</span><strong>2</strong></div>
            <div><span>More Info Requested</span><strong>4</strong></div>
          </div>
        </Card>
      </div>
    </section>
  );
}

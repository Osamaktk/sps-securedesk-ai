import { useEffect, useState } from 'react';
import ChannelHealth from '../../components/dashboard/ChannelHealth';
import AsyncState from '../../components/common/AsyncState';
import DashboardStats from '../../components/dashboard/DashboardStats';
import HighRiskPanel from '../../components/dashboard/HighRiskPanel';
import RecentTickets from '../../components/dashboard/RecentTickets';
import SLAOverview from '../../components/dashboard/SLAOverview';
import TicketSourceChart from '../../components/dashboard/TicketSourceChart';
import Badge from '../../components/common/Badge';
import { getTickets } from '../../services/ticketService.js';

const sourceMeta = {
  email: { label: 'Email', color: '#2563eb' },
  portal_form: { label: 'Portal Form', color: '#0f766e' },
  chat: { label: 'Chat', color: '#7c3aed' },
};

function isOpen(ticket) {
  return !['resolved', 'closed'].includes(ticket.status);
}

function buildAgentDashboardReports(tickets) {
  const totalTickets = tickets.length;
  const openTickets = tickets.filter(isOpen).length;
  const slaBreached = tickets.filter(
    (ticket) => isOpen(ticket) && ticket.sla === 'SLA breached',
  ).length;
  const slaCompliance =
    totalTickets > 0 ? Math.max(0, Math.round(((totalTickets - slaBreached) / totalTickets) * 100)) : 100;

  return {
    dashboardStats: {
      totalTickets,
      openTickets,
      slaCompliance,
      highRiskRequests: tickets.filter((ticket) => ticket.riskLevel === 'high').length,
    },
    ticketsBySource: Object.entries(sourceMeta).map(([key, meta]) => ({
      label: meta.label,
      value: tickets.filter((ticket) => ticket.source === key).length,
      color: meta.color,
    })),
    slaPerformance: [
      { period: 'Current', met: slaCompliance },
      { period: 'Target', met: 95 },
      { period: 'Previous', met: slaCompliance },
    ],
  };
}

export default function AgentDashboard() {
  const [tickets, setTickets] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let isMounted = true;
    setError('');
    setIsLoading(true);

    getTickets().then((ticketData) => {
      if (!isMounted) return;
      setTickets(ticketData);
      setIsLoading(false);
    }).catch(() => {
      if (isMounted) setError('The operations data could not be loaded from the backend.');
      if (isMounted) setIsLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, [reloadKey]);

  if (error) return <AsyncState type="error" title="Dashboard unavailable" description={error} onAction={() => setReloadKey((value) => value + 1)} />;
  if (isLoading) return <AsyncState title="Loading dashboard" description="Preparing operations metrics and ticket activity." />;

  const reports = buildAgentDashboardReports(tickets);

  return (
    <section className="page agent-dashboard">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Service operations</p>
          <h1>SecureDesk AI Dashboard</h1>
          <p>Unified helpdesk operations across email, web form, and AI chat.</p>
        </div>
        <Badge tone="green">Live systems operational</Badge>
      </div>

      <div className="dashboard-info-banner">
        <span className="dashboard-info-banner__icon" aria-hidden="true">
          i
        </span>
        <div>
          <strong>All channels feed one ticket system and one timeline.</strong>
          <p>
            Email, portal form, and AI chat requests share the same service
            workflow and reporting model.
          </p>
        </div>
      </div>

      <DashboardStats tickets={tickets} />
      <TicketSourceChart sources={reports.ticketsBySource} />

      <div className="dashboard-main-grid">
        <RecentTickets tickets={tickets} />
        <HighRiskPanel tickets={tickets} />
      </div>

      <div className="dashboard-secondary-grid">
        <SLAOverview
          compliance={reports.dashboardStats.slaCompliance}
          performance={reports.slaPerformance}
        />
        <ChannelHealth />
      </div>
    </section>
  );
}

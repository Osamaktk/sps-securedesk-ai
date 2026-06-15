import Badge from '../common/Badge';

const statusTones = {
  New: 'blue',
  'In Progress': 'blue',
  'Waiting Approval': 'amber',
  'Waiting User': 'amber',
  Resolved: 'green',
  Closed: 'gray',
};

export default function TicketStatusBadge({ status }) {
  return <Badge tone={statusTones[status] || 'gray'}>{status}</Badge>;
}

import AdminManagementPage from '../../components/common/AdminManagementPage';

const rows = [
  { id: 'SLA-01', priority: 'Critical', response: '30 minutes', resolution: '4 hours', escalation: '15 minutes' },
  { id: 'SLA-02', priority: 'High', response: '2 hours', resolution: '8 hours', escalation: '1 hour' },
  { id: 'SLA-03', priority: 'Medium', response: '8 hours', resolution: '2 business days', escalation: '4 hours' },
  { id: 'SLA-04', priority: 'Low', response: '1 business day', resolution: '5 business days', escalation: '2 business days' },
];

export default function SLASettings() {
  return <AdminManagementPage title="SLA Settings" description="Review priority-based response, resolution, and escalation targets." actionLabel="Add SLA Policy" rows={rows} columns={[{ key: 'priority', label: 'Priority' }, { key: 'response', label: 'Response Target' }, { key: 'resolution', label: 'Resolution Target' }, { key: 'escalation', label: 'Escalation' }]} />;
}

import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';

// Values match backend/services/sla_service.py SLA_HOURS dict exactly
const SLA_POLICIES = [
  { id: 'critical', priority: 'Critical', response: '30 minutes',    resolution: '4 hours',   escalation: '15 minutes'    },
  { id: 'high',     priority: 'High',     response: '2 hours',       resolution: '8 hours',   escalation: '1 hour'        },
  { id: 'medium',   priority: 'Medium',   response: '8 hours',       resolution: '24 hours',  escalation: '4 hours'       },
  { id: 'low',      priority: 'Low',      response: '1 business day', resolution: '72 hours', escalation: '2 business days'},
];

export default function SLASettings() {
  return (
    <section className="page admin-management-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">System administration</p>
          <h1>SLA Settings</h1>
          <p>Priority-based response and resolution targets enforced by the backend SLA engine.</p>
        </div>
      </div>

      <Card
        className="admin-management-card"
        title="SLA policy configuration"
        subtitle="Resolution deadlines are computed from ticket creation time in backend/services/sla_service.py."
        actions={<Badge tone="blue">{SLA_POLICIES.length} policies</Badge>}
      >
        <div className="admin-management-table-wrap">
          <table className="admin-management-table">
            <caption className="visually-hidden">SLA policy configuration</caption>
            <thead>
              <tr>
                <th scope="col">Priority</th>
                <th scope="col">Response Target</th>
                <th scope="col">Resolution Target</th>
                <th scope="col">Escalation</th>
              </tr>
            </thead>
            <tbody>
              {SLA_POLICIES.map((policy) => (
                <tr key={policy.id}>
                  <td>{policy.priority}</td>
                  <td>{policy.response}</td>
                  <td>{policy.resolution}</td>
                  <td>{policy.escalation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </section>
  );
}
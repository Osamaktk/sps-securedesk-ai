import Badge from '../common/Badge';
import Card from '../common/Card';

export default function SLAOverview({ performance, compliance }) {
  return (
    <Card
      className="dashboard-panel sla-overview"
      title="SLA Overview"
      subtitle="Weekly response and resolution target performance."
      actions={<Badge tone="green">{compliance}% compliant</Badge>}
    >
      <div className="sla-overview__summary">
        <div>
          <strong>{compliance}%</strong>
          <span>Current compliance</span>
        </div>
        <p>Target: 95% or higher across all priority levels.</p>
      </div>
      <div className="sla-overview__bars">
        {performance.map((item) => (
          <div className="sla-overview__row" key={item.period}>
            <div>
              <span>{item.period}</span>
              <strong>{item.met}%</strong>
            </div>
            <div
              className="sla-overview__track"
              role="progressbar"
              aria-label={`${item.period} SLA compliance`}
              aria-valuemin="0"
              aria-valuemax="100"
              aria-valuenow={item.met}
            >
              <span style={{ width: `${item.met}%` }} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

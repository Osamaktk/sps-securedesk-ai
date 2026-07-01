import { CATEGORIES } from '../../config/constants.js';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';

const CATEGORY_META = {
  cloud:          { team: 'Cloud Operations',    priority: 'Medium', risk: 'Standard' },
  cybersecurity:  { team: 'Security Operations', priority: 'High',   risk: 'High'     },
  identity_access:{ team: 'Identity Governance', priority: 'High',   risk: 'High'     },
  devops:         { team: 'DevOps Platform',     priority: 'Medium', risk: 'Standard' },
  internship_hr:  { team: 'Workplace Support',   priority: 'Low',    risk: 'Standard' },
  general_it:     { team: 'Workplace Support',   priority: 'Medium', risk: 'Standard' },
};

export default function Categories() {
  return (
    <section className="page admin-management-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">System administration</p>
          <h1>Categories</h1>
          <p>Request categories and default routing rules enforced by the backend ticket classifier.</p>
        </div>
      </div>

      <Card
        className="admin-management-card"
        title="Category configuration"
        subtitle="System-defined categories used for AI classification and ticket routing."
        actions={<Badge tone="blue">{CATEGORIES.length} categories</Badge>}
      >
        <div className="admin-management-table-wrap">
          <table className="admin-management-table">
            <caption className="visually-hidden">Category configuration</caption>
            <thead>
              <tr>
                <th scope="col">Category</th>
                <th scope="col">Assigned Team</th>
                <th scope="col">Default Priority</th>
                <th scope="col">Risk Level</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {CATEGORIES.map((cat) => {
                const meta = CATEGORY_META[cat.value] || {};
                return (
                  <tr key={cat.value}>
                    <td>{cat.label}</td>
                    <td>{meta.team}</td>
                    <td>{meta.priority}</td>
                    <td>{meta.risk}</td>
                    <td><Badge tone="blue">Active</Badge></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </section>
  );
}
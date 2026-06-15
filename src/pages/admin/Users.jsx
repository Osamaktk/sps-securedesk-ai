import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import { mockUsers } from '../../data/mockUsers.js';

export default function Users() {
  return (
    <section className="page users-admin-page">
      <div className="page-heading">
        <div><p className="eyebrow">System administration</p><h1>Users</h1><p>Review mock users, roles, departments, and account status.</p></div>
        <Button disabled>Add User</Button>
      </div>
      <div className="future-integration-note"><span aria-hidden="true">API</span><div><strong>Future backend integration</strong><p>User provisioning and role changes will require secured identity APIs.</p></div></div>
      <Card title="User Management" subtitle="Static user directory for frontend review." actions={<Badge tone="blue">{mockUsers.length} users</Badge>}>
        <div className="admin-management-table-wrap">
          <table className="admin-management-table">
            <caption className="visually-hidden">Mock user management records</caption>
            <thead><tr><th scope="col">User</th><th scope="col">Email</th><th scope="col">Role</th><th scope="col">Department</th><th scope="col">Status</th><th scope="col">Action</th></tr></thead>
            <tbody>{mockUsers.map((user) => <tr key={user.id}><td><strong>{user.name}</strong></td><td>{user.email}</td><td>{user.role.replaceAll('_', ' ')}</td><td>{user.department}</td><td><Badge tone="green">{user.status}</Badge></td><td><Button variant="outline" disabled>Manage</Button></td></tr>)}</tbody>
          </table>
        </div>
      </Card>
    </section>
  );
}

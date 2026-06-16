import AdminManagementPage from '../../components/common/AdminManagementPage';

const rows = [
  { id: 'CAT-01', category: 'Cloud', team: 'Cloud Operations', defaultPriority: 'Medium', status: 'Active' },
  { id: 'CAT-02', category: 'Cybersecurity', team: 'Security Operations', defaultPriority: 'High', status: 'Active' },
  { id: 'CAT-03', category: 'Identity and Access', team: 'Identity Governance', defaultPriority: 'High', status: 'Active' },
  { id: 'CAT-04', category: 'DevOps', team: 'DevOps Platform', defaultPriority: 'Medium', status: 'Active' },
  { id: 'CAT-05', category: 'Internship/HR', team: 'Workplace Support', defaultPriority: 'Low', status: 'Active' },
  { id: 'CAT-06', category: 'General IT', team: 'Workplace Support', defaultPriority: 'Medium', status: 'Active' },
];

export default function Categories() {
  return <AdminManagementPage title="Categories" description="Configure request categories and default routing teams." actionLabel="Add Category" rows={rows} columns={[{ key: 'category', label: 'Category' }, { key: 'team', label: 'Assigned Team' }, { key: 'defaultPriority', label: 'Default Priority' }, { key: 'status', label: 'Status' }]} />;
}

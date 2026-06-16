import AdminManagementPage from '../../components/common/AdminManagementPage';

const rows = [
  { id: 'KB-1003', article: 'Password Reset', topic: 'Identity and Access', status: 'Published', owner: 'Workplace Support' },
  { id: 'KB-1042', article: 'Privileged Access Requests', topic: 'Cybersecurity', status: 'Published', owner: 'Security Operations' },
  { id: 'KB-1108', article: 'VPN Troubleshooting', topic: 'Cloud', status: 'Published', owner: 'Cloud Operations' },
  { id: 'KB-1210', article: 'Intern Onboarding', topic: 'Internship/HR', status: 'Draft', owner: 'Workplace Support' },
];

export default function KnowledgeBase() {
  return <AdminManagementPage title="Knowledge Base" description="Manage approved support articles used by agents and SecureDesk AI." actionLabel="Create Article" rows={rows} columns={[{ key: 'id', label: 'Article ID' }, { key: 'article', label: 'Article' }, { key: 'topic', label: 'Topic' }, { key: 'status', label: 'Status' }, { key: 'owner', label: 'Owner' }]} />;
}

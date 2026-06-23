import { useEffect, useState } from 'react';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import userService from '../../services/userService';

const STATUS_LABELS = {
  true: 'Active',
  false: 'Inactive',
};

const STATUS_TONES = {
  true: 'green',
  false: 'red',
};

function roleLabel(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function Users() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [modalData, setModalData] = useState({
    email: '',
    full_name: '',
    password: '',
    role: 'employee',
    is_active: true,
  });
  const [saving, setSaving] = useState(false);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [usersData, rolesData] = await Promise.all([
        userService.getUsers(),
        userService.getRoles(),
      ]);
      setUsers(usersData);
      setRoles(rolesData);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load users. Make sure you are logged in as Administrator.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function openCreateModal() {
    setEditingUser(null);
    setModalData({ email: '', full_name: '', password: '', role: 'employee', is_active: true });
    setShowModal(true);
  }

  function openEditModal(user) {
    setEditingUser(user);
    setModalData({
      email: user.email,
      full_name: user.full_name,
      password: '',
      role: user.role,
      is_active: user.is_active,
    });
    setShowModal(true);
  }

  function closeModal() {
    setShowModal(false);
    setEditingUser(null);
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingUser) {
        const updatePayload = {};
        if (modalData.full_name !== editingUser.full_name) updatePayload.full_name = modalData.full_name;
        if (modalData.role !== editingUser.role) updatePayload.role = modalData.role;
        if (modalData.is_active !== editingUser.is_active) updatePayload.is_active = modalData.is_active;
        if (Object.keys(updatePayload).length > 0) {
          await userService.updateUser(editingUser.id, updatePayload);
        }
      } else {
        await userService.createUser(modalData);
      }
      closeModal();
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save user.');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(userId, userEmail) {
    if (!window.confirm(`Are you sure you want to delete user "${userEmail}"? This cannot be undone.`)) {
      return;
    }
    try {
      await userService.deleteUser(userId);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete user.');
    }
  }

  function handleModalChange(field, value) {
    setModalData((prev) => ({ ...prev, [field]: value }));
  }

  if (loading) {
    return (
      <section className="page users-admin-page">
        <div className="page-heading">
          <div><p className="eyebrow">System administration</p><h1>Users</h1><p>Loading users...</p></div>
        </div>
      </section>
    );
  }

  return (
    <section className="page users-admin-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">System administration</p>
          <h1>Users</h1>
          <p>Manage user accounts and roles.</p>
        </div>
        <Button onClick={openCreateModal}>Add User</Button>
      </div>

      {error && (
        <div className="alert alert--error" role="alert">
          <p>{error}</p>
          <Button variant="outline" onClick={() => setError(null)}>Dismiss</Button>
        </div>
      )}

      {/* Users Table */}
      <Card
        title="User Accounts"
        subtitle="All registered users in the system."
        actions={<Badge tone="blue">{users.length} users</Badge>}
      >
        <div className="admin-management-table-wrap">
          <table className="admin-management-table">
            <caption className="visually-hidden">User accounts</caption>
            <thead>
              <tr>
                <th scope="col">Name</th>
                <th scope="col">Email</th>
                <th scope="col">Role</th>
                <th scope="col">Status</th>
                <th scope="col">Action</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td><strong>{user.full_name}</strong></td>
                  <td>{user.email}</td>
                  <td><Badge value={user.role}>{roleLabel(user.role)}</Badge></td>
                  <td><Badge tone={STATUS_TONES[user.is_active]}>{STATUS_LABELS[user.is_active]}</Badge></td>
                  <td className="admin-actions-cell">
                    <Button variant="outline" onClick={() => openEditModal(user)}>Edit</Button>
                    <Button variant="outline" onClick={() => handleDelete(user.id, user.email)}>Delete</Button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '2rem', color: '#888' }}>
                    No users found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Role Model Table */}
      <Card
        title="Role Model"
        subtitle="Backend roles available for authentication and route guards."
        actions={<Badge tone="blue">{roles.length} roles</Badge>}
      >
        <div className="admin-management-table-wrap">
          <table className="admin-management-table">
            <caption className="visually-hidden">Backend role model records</caption>
            <thead>
              <tr>
                <th scope="col">Role</th>
                <th scope="col">Value</th>
                <th scope="col">Access</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => (
                <tr key={role.value}>
                  <td><strong>{role.name}</strong></td>
                  <td><code>{role.value}</code></td>
                  <td>{role.access}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="modal-backdrop" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal__header">
              <h2>{editingUser ? 'Edit User' : 'Add User'}</h2>
              <p>{editingUser ? 'Update user account details and role.' : 'Create a new user account.'}</p>
              <button className="modal__close" onClick={closeModal} aria-label="Close">&times;</button>
            </div>
            <form onSubmit={handleSave}>
              <div className="modal__body">
                <div className="request-field">
                  <span>Full Name</span>
                  <input
                    id="user-full-name"
                    type="text"
                    required
                    value={modalData.full_name}
                    onChange={(e) => handleModalChange('full_name', e.target.value)}
                  />
                </div>
                <div className="request-field">
                  <span>Email</span>
                  <input
                    id="user-email"
                    type="email"
                    required
                    disabled={!!editingUser}
                    value={modalData.email}
                    onChange={(e) => handleModalChange('email', e.target.value)}
                  />
                </div>
                {!editingUser && (
                  <div className="request-field">
                    <span>Password</span>
                    <input
                      id="user-password"
                      type="password"
                      required
                      minLength={8}
                      value={modalData.password}
                      onChange={(e) => handleModalChange('password', e.target.value)}
                    />
                  </div>
                )}
                <div className="request-field">
                  <span>Role</span>
                  <select
                    id="user-role"
                    value={modalData.role}
                    onChange={(e) => handleModalChange('role', e.target.value)}
                  >
                    {roles.map((role) => (
                      <option key={role.value} value={role.value}>{role.name}</option>
                    ))}
                  </select>
                </div>
                <div className="request-field" style={{ flexDirection: 'row', alignItems: 'center', gap: '8px' }}>
                  <label htmlFor="user-active" style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      id="user-active"
                      type="checkbox"
                      checked={modalData.is_active}
                      onChange={(e) => handleModalChange('is_active', e.target.checked)}
                    />
                    <span style={{ fontSize: '10px', fontWeight: 800, color: 'var(--sps-deep-navy)' }}>Active account</span>
                  </label>
                </div>
              </div>
              <div className="modal__footer">
                <Button type="button" variant="outline" onClick={closeModal}>Cancel</Button>
                <Button type="submit" disabled={saving}>
                  {saving ? 'Saving...' : editingUser ? 'Update User' : 'Create User'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
import { useState, useEffect, useCallback } from 'react';
import kbService from '../../services/kbService.js';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';

export default function KnowledgeBase() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ filename: '', content: '' });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');
  const [deletingFile, setDeletingFile] = useState(null);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const docs = await kbService.listDocuments();
      setDocuments(docs);
    } catch {
      setError('Could not load documents. Make sure the AI service is running on port 8001.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadDocuments(); }, [loadDocuments]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setFormError('');
    setSubmitting(true);
    try {
      await kbService.createDocument(form.filename.trim(), form.content.trim());
      setShowForm(false);
      setForm({ filename: '', content: '' });
      await loadDocuments();
    } catch (err) {
      setFormError(err.response?.data?.detail || 'Failed to create document. Check that the filename ends in .txt and does not already exist.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete "${filename}" from the knowledge base? This will remove it from AI chat responses.`)) return;
    setDeletingFile(filename);
    try {
      await kbService.deleteDocument(filename);
      await loadDocuments();
    } catch {
      alert('Failed to delete document.');
    } finally {
      setDeletingFile(null);
    }
  };

  const updateField = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const cancelForm = () => {
    setShowForm(false);
    setForm({ filename: '', content: '' });
    setFormError('');
  };

  return (
    <section className="page admin-management-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">System administration</p>
          <h1>Knowledge Base</h1>
          <p>Manage support documents indexed for SecureDesk AI chat. Changes take effect immediately.</p>
        </div>
        {!showForm && (
          <Button onClick={() => setShowForm(true)}>Add Document</Button>
        )}
      </div>

      {showForm && (
        <Card className="admin-management-card" title="Add KB document" subtitle="Only .txt files are supported. Content is indexed immediately into the AI vector store.">
          <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '0.5rem 0' }}>
            <label>
              Filename <span style={{ color: 'var(--color-text-subtle)', fontSize: '0.85rem' }}>(must end in .txt)</span>
              <input
                name="filename"
                required
                placeholder="e.g. VPN Setup Guide.txt"
                value={form.filename}
                onChange={updateField}
              />
            </label>
            <label>
              Document content
              <textarea
                name="content"
                required
                rows={10}
                placeholder="Paste the full document text here…"
                value={form.content}
                onChange={updateField}
                style={{ resize: 'vertical', fontFamily: 'monospace', fontSize: '0.85rem' }}
              />
            </label>
            {formError && <p className="form-error" role="alert">{formError}</p>}
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <Button type="submit" disabled={submitting}>
                {submitting ? 'Uploading…' : 'Upload Document'}
              </Button>
              <Button variant="outline" type="button" onClick={cancelForm}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      <Card
        className="admin-management-card"
        title="Indexed documents"
        subtitle="Documents available to SecureDesk AI for grounded chat responses."
        actions={<Badge tone="blue">{documents.length} documents</Badge>}
      >
        {loading && <p style={{ padding: '1rem', color: 'var(--color-text-subtle)' }}>Loading documents…</p>}
        {error && <p className="form-error" role="alert" style={{ padding: '1rem' }}>{error}</p>}
        {!loading && !error && (
          <div className="admin-management-table-wrap">
            <table className="admin-management-table">
              <caption className="visually-hidden">Knowledge base documents</caption>
              <thead>
                <tr>
                  <th scope="col">Filename</th>
                  <th scope="col">Chunks</th>
                  <th scope="col">Indexed</th>
                  <th scope="col">Action</th>
                </tr>
              </thead>
              <tbody>
                {documents.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-subtle)' }}>
                      No documents indexed yet. Use the Add Document button above.
                    </td>
                  </tr>
                )}
                {documents.map((doc) => (
                  <tr key={doc.filename}>
                    <td>{doc.filename}</td>
                    <td>{doc.chunk_count}</td>
                    <td>{doc.created_at ? new Date(doc.created_at).toLocaleDateString() : '—'}</td>
                    <td>
                      <Button
                        variant="outline"
                        onClick={() => handleDelete(doc.filename)}
                        disabled={deletingFile === doc.filename}
                      >
                        {deletingFile === doc.filename ? 'Deleting…' : 'Delete'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </section>
  );
}
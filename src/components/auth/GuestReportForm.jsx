import { useState } from 'react';
import ticketService from '../../services/ticketService.js';
import { useAuth } from '../../context/AuthContext';
import { enhanceDescription } from '../../services/aiService';

const CATEGORIES = [
  'Cloud',
  'Cybersecurity',
  'Identity and Access',
  'DevOps',
  'Internship/HR',
  'General IT',
];

export default function GuestReportForm() {
  const { user } = useAuth();
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [priority, setPriority] = useState('medium');
  const [files, setFiles] = useState([]);
  const [email, setEmail] = useState(user?.email || '');
  const [aiEnhancedDescription, setAiEnhancedDescription] = useState(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const onFilesChange = (e) => {
    setFiles(Array.from(e.target.files || []));
  };

  const handleEnhanceDescription = async () => {
    if (!subject.trim() || !description.trim()) return;
    setIsEnhancing(true);
    try {
      const response = await enhanceDescription(subject.trim(), description.trim());
      setAiEnhancedDescription(response.summary || response.enhanced_description || response.description);
    } catch {
      setError('Could not enhance description with AI. You can still submit your original description.');
    } finally {
      setIsEnhancing(false);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!subject.trim() || !description.trim() || !category || !email.trim()) {
      setError('Please complete the required fields.');
      return;
    }

    setIsSubmitting(true);
    try {
      const finalDescription = (aiEnhancedDescription || description).trim();
      const payload = {
        subject: subject.trim(),
        description: finalDescription,
        category,
        priority,
        requester_email: email.trim(),
      };

      // create ticket from portal form
      const ticket = await ticketService.createTicketFromForm(payload);

      // upload attachments if any
      if (files.length && ticket?.id) {
        // limit: 5 files
        const uploadFiles = files.slice(0, 5);
        for (const f of uploadFiles) {
          try {
            await ticketService.uploadFile(ticket.id, f);
          } catch (uploadErr) {
            console.warn('Attachment upload failed', uploadErr);
          }
        }
      }

      setMessage(`Submitted — ticket #${ticket.ticketNumber || ticket.id || 'created'}. We will follow up via email.`);
      setSubject('');
      setDescription('');
      setFiles([]);
      if (!user) setEmail('');
    } catch (err) {
      console.error(err);
      setError('Failed to submit report. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="guest-form" onSubmit={submit}>
      <h3>Guest reporting form</h3>
      <label>
        Subject / title (required)
        <input value={subject} onChange={(e) => setSubject(e.target.value)} required />
      </label>

      <label>
        Description (required)
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} required rows={5} />
      </label>

      <label>
        Category (required)
        <select value={category} onChange={(e) => setCategory(e.target.value)} required>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </label>

      <label>
        Priority hint (optional)
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </label>

      <label>
        Attachments (screenshots, logs) — max 5 files
        <input type="file" onChange={onFilesChange} multiple />
      </label>

      <label>
        Contact email {user ? '(prefilled)' : '(required)'}
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={!!user}
        />
      </label>

      <div className="guest-form__ai-enhance" style={{ margin: '15px 0' }}>
        <button
          type="button"
          className="secondary-button"
          onClick={handleEnhanceDescription}
          disabled={isEnhancing || !subject.trim() || !description.trim()}
          style={{ width: '100%' }}
        >
          {isEnhancing ? 'Enhancing...' : '✨ Enhance Description with AI'}
        </button>
        {aiEnhancedDescription && (
          <div className="ai-enhanced-preview" style={{ marginTop: '12px' }}>
            <h4 style={{ fontSize: '0.9rem', marginBottom: '6px', fontWeight: '600' }}>AI Enhanced Description Preview:</h4>
            <textarea
              className="chat-ticket-card__textarea"
              value={aiEnhancedDescription}
              readOnly
              rows={5}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', backgroundColor: '#f9f9f9' }}
            />
            <button
              type="button"
              className="secondary-button"
              onClick={() => setAiEnhancedDescription(null)}
              style={{ marginTop: '6px', fontSize: '0.8rem' }}
            >
              Clear AI Enhancement
            </button>
          </div>
        )}
      </div>

      {error && <p className="form-error" role="alert">{error}</p>}
      {message && <p className="form-success">{message}</p>}

      <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
        <button className="secondary-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting...' : 'Submit report'}
        </button>
      </div>
    </form>
  );
}

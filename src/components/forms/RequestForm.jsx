import { useState } from 'react';
import Button from '../common/Button';
import CategorySelect from './CategorySelect';
import FileUpload from './FileUpload';

const priorityOptions = ['Low', 'Medium', 'High', 'Critical'];

const initialForm = {
  subject: '',
  description: '',
  category: '',
  priority: 'Medium',
  requesterEmail: 'amina.qureshi@northstar.example',
};

export default function RequestForm({ onSubmit }) {
  const [form, setForm] = useState(initialForm);
  const [attachments, setAttachments] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateField = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const submitForm = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    await onSubmit({
      ...form,
      requesterName: 'Amina Qureshi',
      aiSummary: form.description,
      attachments,
    });
    setIsSubmitting(false);
  };

  return (
    <form className="request-form" onSubmit={submitForm}>
      <div className="request-form__grid">
        <label className="request-field request-field--full">
          <span>Subject / title</span>
          <input
            name="subject"
            required
            value={form.subject}
            placeholder="Briefly describe what you need help with"
            onChange={updateField}
          />
        </label>

        <label className="request-field request-field--full">
          <span>Description</span>
          <textarea
            name="description"
            required
            value={form.description}
            placeholder="Include the impact, relevant error messages, and steps already tried"
            onChange={updateField}
          />
          <small>Do not include passwords, recovery codes, or other secrets.</small>
        </label>

        <CategorySelect value={form.category} onChange={updateField} />

        <label className="request-field">
          <span>Priority hint</span>
          <select name="priority" value={form.priority} onChange={updateField}>
            {priorityOptions.map((priority) => (
              <option key={priority} value={priority}>
                {priority}
              </option>
            ))}
          </select>
          <small>The service desk will confirm the final priority.</small>
        </label>

        <label className="request-field request-field--full">
          <span>Contact email</span>
          <input
            name="requesterEmail"
            type="email"
            required
            value={form.requesterEmail}
            onChange={updateField}
          />
        </label>

        <div className="request-field request-field--full">
          <FileUpload
            onUploaded={(attachment) =>
              setAttachments((current) => [...current, attachment])
            }
          />
        </div>
      </div>

      <div className="request-form__footer">
        <p>Submitting creates a mock portal-form ticket in the local session.</p>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting request...' : 'Submit Request'}
        </Button>
      </div>
    </form>
  );
}

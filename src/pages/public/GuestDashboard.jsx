import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import ticketService from '../../services/ticketService.js';
import { STATUS_COLORS, CATEGORIES } from '../../config/constants.js';

function labelize(value) {
  return String(value || '')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function StatusBadge({ status }) {
  const color = STATUS_COLORS[status] || 'bg-gray-100 text-gray-600';
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold ${color}`}>
      {labelize(status)}
    </span>
  );
}

function Timeline({ events = [] }) {
  if (!events.length) {
    return <p className="text-xs text-gray-400">No activity yet.</p>;
  }
  return (
    <ul className="space-y-2">
      {events.map((ev) => (
        <li key={ev.id} className="text-sm">
          <span className="font-medium text-gray-700">{labelize(ev.event_type)}</span>
          <span className="text-gray-400"> · {ev.actor_email || 'System'}</span>
          {ev.content ? <p className="text-gray-600">{ev.content}</p> : null}
        </li>
      ))}
    </ul>
  );
}

function TicketCard({ ticket, token, onReplied }) {
  const [expanded, setExpanded] = useState(false);
  const [reply, setReply] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const locked = ['closed', 'duplicate', 'resolved'].includes(ticket.status);

  const submitReply = async (e) => {
    e.preventDefault();
    if (!reply.trim()) return;
    setSending(true);
    setError('');
    try {
      await ticketService.guestReply(token, ticket.ticket_number, reply.trim());
      setReply('');
      onReplied();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to send reply.');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-mono text-sm text-gray-500">{ticket.ticket_number}</p>
          <h3 className="text-base font-semibold text-gray-800">{ticket.subject}</h3>
        </div>
        <StatusBadge status={ticket.status} />
      </div>
      <p className="mt-1 text-sm text-gray-500">
        {labelize(ticket.category)} · {labelize(ticket.priority)} · {labelize(ticket.source)}
      </p>

      <div className="mt-3 flex gap-3 text-sm">
        <button
          type="button"
          className="text-blue-600 hover:underline"
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? 'Hide activity' : 'View activity'}
        </button>
      </div>

      {expanded ? (
        <div className="mt-3 border-t border-gray-100 pt-3">
          <Timeline events={ticket.timeline_events || ticket.timeline || []} />
        </div>
      ) : null}

      {!locked ? (
        <form onSubmit={submitReply} className="mt-3 border-t border-gray-100 pt-3">
          <textarea
            value={reply}
            onChange={(e) => setReply(e.target.value)}
            rows={2}
            placeholder="Write a reply to the support team…"
            className="w-full rounded border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : null}
          <button
            type="submit"
            disabled={sending}
            className="mt-2 rounded bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {sending ? 'Sending…' : 'Send reply'}
          </button>
        </form>
      ) : (
        <p className="mt-3 border-t border-gray-100 pt-3 text-xs text-gray-400">
          This ticket is {labelize(ticket.status)} and no longer accepts replies.
        </p>
      )}
    </div>
  );
}

function NewTicketForm({ token, onCreated }) {
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0].value);
  const [priority, setPriority] = useState('medium');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    if (!subject.trim()) return;
    setSubmitting(true);
    setError('');
    setSuccess('');
    try {
      await ticketService.guestCreateTicket(token, {
        source: 'portal_form',
        subject: subject.trim(),
        description: description.trim(),
        category,
        priority,
      });
      setSubject('');
      setDescription('');
      setSuccess('Ticket submitted. It now appears in your dashboard below.');
      onCreated();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to submit ticket.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-base font-semibold text-gray-800">Submit a new request</h3>
      <input
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
        placeholder="Subject"
        className="mb-2 w-full rounded border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none"
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={3}
        placeholder="Describe your issue…"
        className="mb-2 w-full rounded border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none"
      />
      <div className="mb-3 flex gap-2">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="flex-1 rounded border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none"
        >
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>{c.label}</option>
          ))}
        </select>
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="flex-1 rounded border border-gray-300 p-2 text-sm focus:border-blue-500 focus:outline-none"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
      {error ? <p className="mb-2 text-xs text-red-600">{error}</p> : null}
      {success ? <p className="mb-2 text-xs text-green-600">{success}</p> : null}
      <button
        type="submit"
        disabled={submitting}
        className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {submitting ? 'Submitting…' : 'Submit request'}
      </button>
    </form>
  );
}

export default function GuestDashboard() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    if (!token) {
      setError('Missing or invalid guest link. Please use the link from your acknowledgment email.');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await ticketService.getGuestDashboard(token);
      setTickets(data);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not load your tickets. The link may have expired.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="mx-auto max-w-3xl px-4">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-800">Your Support Tickets</h1>
          <p className="text-sm text-gray-500">
            Signed in with a secure link — no password required.
          </p>
        </div>

        {loading ? (
          <p className="text-center text-gray-500">Loading your tickets…</p>
        ) : error ? (
          <div className="rounded border border-red-200 bg-red-50 p-4 text-center text-red-700">{error}</div>
        ) : (
          <>
            <div className="mb-6">
              <NewTicketForm token={token} onCreated={load} />
            </div>
            {tickets.length === 0 ? (
              <p className="text-center text-gray-500">You have no tickets yet.</p>
            ) : (
              <div className="space-y-4">
                {tickets.map((ticket) => (
                  <TicketCard key={ticket.id} ticket={ticket} token={token} onReplied={load} />
                ))}
              </div>
            )}
            <p className="mt-8 text-center text-xs text-gray-400">
              This link is private to you. Keep it safe — anyone with the link can view and reply to your tickets.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
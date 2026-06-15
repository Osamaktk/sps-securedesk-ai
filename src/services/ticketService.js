import { mockTickets } from '../data/mockTickets.js';
import { cloneMockData, mockApiError, mockApiResponse } from './api.js';

let ticketStore = cloneMockData(mockTickets);

function matchesFilter(ticket, key, expected) {
  if (expected === undefined || expected === null || expected === '') return true;

  const values = Array.isArray(expected) ? expected : [expected];
  return values.some(
    (value) => String(ticket[key]).toLowerCase() === String(value).toLowerCase(),
  );
}

function nextTicketId() {
  const highestId = ticketStore.reduce((highest, ticket) => {
    const number = Number(ticket.id.split('-').at(-1));
    return Number.isNaN(number) ? highest : Math.max(highest, number);
  }, 0);

  return `SPS-2026-${String(highestId + 1).padStart(3, '0')}`;
}

function createTicket(data = {}, source) {
  const now = new Date().toISOString();
  const id = nextTicketId();

  const ticket = {
    id,
    subject: data.subject || 'New support request',
    requesterName: data.requesterName || 'Mock Requester',
    requesterEmail: data.requesterEmail || 'requester@example.com',
    source,
    category: data.category || 'General IT',
    priority: data.priority || 'Medium',
    risk: data.risk || 'Normal',
    status: 'New',
    assignedTeam: data.assignedTeam || 'Service Desk',
    sla: data.sla || '8 hours remaining',
    updatedAt: now,
    createdAt: now,
    aiSummary: data.aiSummary || data.summary || 'Awaiting agent review.',
    attachments: cloneMockData(data.attachments || []),
    timeline: [
      {
        id: `${id}-TL-1`,
        type: source === 'chat' ? 'Chat escalation note' : 'Form submitted',
        actor: source === 'chat' ? 'SecureDesk AI' : data.requesterName || 'Mock Requester',
        message:
          data.timelineMessage ||
          (source === 'chat'
            ? 'Ticket created from an escalated mock chat conversation.'
            : 'Ticket created from the mock portal request form.'),
        createdAt: now,
      },
    ],
  };

  ticketStore = [ticket, ...ticketStore];
  return ticket;
}

export function getTickets() {
  return mockApiResponse(ticketStore);
}

export function getTicketById(id) {
  const ticket = ticketStore.find((item) => item.id === id);
  return mockApiResponse(ticket || null);
}

export function filterTickets(filters = {}) {
  const searchTerm = String(filters.search || '').trim().toLowerCase();
  const filterKeys = [
    'source',
    'category',
    'priority',
    'risk',
    'status',
    'assignedTeam',
    'requesterEmail',
  ];

  const results = ticketStore.filter((ticket) => {
    const matchesSearch =
      !searchTerm ||
      [ticket.id, ticket.subject, ticket.requesterName, ticket.requesterEmail]
        .join(' ')
        .toLowerCase()
        .includes(searchTerm);

    return (
      matchesSearch &&
      filterKeys.every((key) => matchesFilter(ticket, key, filters[key]))
    );
  });

  return mockApiResponse(results);
}

export function updateTicketStatus(id, status) {
  const ticket = ticketStore.find((item) => item.id === id);
  if (!ticket) return mockApiError(`Ticket ${id} was not found.`, 'TICKET_NOT_FOUND');

  const now = new Date().toISOString();
  const previousStatus = ticket.status;
  ticket.status = status;
  ticket.updatedAt = now;
  ticket.timeline.push({
    id: `${id}-TL-${ticket.timeline.length + 1}`,
    type: 'Status changed',
    actor: 'Mock Service Desk User',
    message: `Changed status from ${previousStatus} to ${status}.`,
    createdAt: now,
  });

  return mockApiResponse(ticket);
}

export function addTicketComment(id, comment) {
  const ticket = ticketStore.find((item) => item.id === id);
  if (!ticket) return mockApiError(`Ticket ${id} was not found.`, 'TICKET_NOT_FOUND');

  const now = new Date().toISOString();
  const commentData =
    typeof comment === 'string' ? { message: comment } : comment || {};
  ticket.updatedAt = now;
  ticket.timeline.push({
    id: `${id}-TL-${ticket.timeline.length + 1}`,
    type: commentData.type || 'Portal comment received',
    actor: commentData.actor || 'Mock Service Desk User',
    message: commentData.message || 'Mock ticket comment.',
    createdAt: now,
  });

  return mockApiResponse(ticket);
}

export function addTicketAttachment(id, attachment) {
  const ticket = ticketStore.find((item) => item.id === id);
  if (!ticket) return mockApiError(`Ticket ${id} was not found.`, 'TICKET_NOT_FOUND');

  const now = new Date().toISOString();
  ticket.updatedAt = now;
  ticket.attachments.push(cloneMockData(attachment));
  ticket.timeline.push({
    id: `${id}-TL-${ticket.timeline.length + 1}`,
    type: 'Portal comment received',
    actor: ticket.requesterName,
    message: `Uploaded attachment: ${attachment.name}.`,
    createdAt: now,
  });

  return mockApiResponse(ticket);
}

export function createTicketFromChat(data) {
  return mockApiResponse(createTicket(data, 'chat'));
}

export function createTicketFromForm(data) {
  return mockApiResponse(createTicket(data, 'portal_form'));
}

export function resetMockTickets() {
  ticketStore = cloneMockData(mockTickets);
  return mockApiResponse(ticketStore);
}

const ticketService = {
  getTickets,
  getTicketById,
  filterTickets,
  updateTicketStatus,
  addTicketComment,
  addTicketAttachment,
  createTicketFromChat,
  createTicketFromForm,
  resetMockTickets,
};

export default ticketService;

import axios from 'axios';
import { AI_URL } from '../config/constants.js';
import { createTicketFromChat } from './ticketService.js';

const aiApi = axios.create({
  baseURL: AI_URL,
});

export function getInitialMessages() {
  return Promise.resolve([
    {
      id: 'WELCOME',
      role: 'assistant',
      type: 'message',
      content:
        'Hi, I am SPS SecureDesk AI. Ask a support question, or I can help prepare a ticket for a human agent.',
      citations: [],
      createdAt: new Date().toISOString(),
    },
  ]);
}

export async function getCategories() {
  const response = await aiApi.get('/api/chat/categories');
  return response.data;
}

export async function sendMessage(session_id, message, user_id, requester_email) {
  const params = { session_id, message, user_id };
  if (requester_email) {
    params.requester_email = requester_email;
  }
  const response = await aiApi.post('/api/chat', params);
  return response.data;
}

export async function createTicketFromEscalation(draft) {
  return createTicketFromChat(draft);
}

export async function enhanceDescription(subject, description) {
  const response = await aiApi.post('/api/summarise', { subject, description });
  return response.data;
}

const chatService = {
  getInitialMessages,
  sendMessage,
  createTicketFromEscalation,
  enhanceDescription,
};

export default chatService;

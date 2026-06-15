import { mockChatMessages, mockChatResponses } from '../data/mockChat.js';
import { mockApiResponse } from './api.js';
import { createTicketFromChat } from './ticketService.js';

function selectMockResponse(message) {
  const normalizedMessage = String(message).toLowerCase();

  if (normalizedMessage.includes('password')) return mockChatResponses.password;
  if (normalizedMessage.includes('vpn')) return mockChatResponses.vpn;
  if (normalizedMessage.includes('phish')) return mockChatResponses.phishing;
  if (normalizedMessage.includes('cloud') || normalizedMessage.includes('vm')) {
    return mockChatResponses.cloud;
  }
  if (normalizedMessage.includes('access')) return mockChatResponses.access;
  if (normalizedMessage.includes('intern') || normalizedMessage.includes('onboard')) {
    return mockChatResponses.onboarding;
  }
  return mockChatResponses.default;
}

export function getInitialMessages() {
  return mockApiResponse(mockChatMessages);
}

export function sendMockMessage(message) {
  const response = selectMockResponse(message);

  return mockApiResponse({
    id: `MSG-${Date.now()}`,
    role: 'assistant',
    type: 'message',
    content: response.content,
    citations: response.citations,
    createdAt: new Date().toISOString(),
  });
}

export function createMockTicketFromChat(summary) {
  const data =
    typeof summary === 'string'
      ? { subject: 'Support request from AI Chat', aiSummary: summary }
      : summary || {};

  return createTicketFromChat(data);
}

const chatService = {
  getInitialMessages,
  sendMockMessage,
  createMockTicketFromChat,
};

export default chatService;

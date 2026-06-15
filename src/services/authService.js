import { currentMockUser } from '../data/mockUsers.js';
import { mockApiResponse } from './api.js';

let activeUser = currentMockUser;

export function mockLogin(credentials = {}) {
  activeUser = {
    ...currentMockUser,
    email: credentials.email || currentMockUser.email,
  };

  return mockApiResponse({
    user: activeUser,
    token: 'mock-securedesk-session-token',
  });
}

export function mockLogout() {
  activeUser = null;
  return mockApiResponse({ success: true });
}

export function getCurrentUser() {
  return mockApiResponse(activeUser);
}

const authService = {
  mockLogin,
  mockLogout,
  getCurrentUser,
};

export default authService;

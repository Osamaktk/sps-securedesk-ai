import api from './api.js';

export async function getNotifications({ limit = 20, unreadOnly = false } = {}) {
  const response = await api.get('/notifications', {
    params: { limit, unread_only: unreadOnly },
  });
  return response.data;
}

export async function getUnreadCount() {
  const response = await api.get('/notifications/unread-count');
  return response.data.unread_count;
}

export async function markAsRead(notificationIds) {
  const response = await api.post('/notifications/mark-read', {
    notification_ids: notificationIds,
  });
  return response.data;
}

export async function markAllAsRead() {
  const response = await api.post('/notifications/mark-all-read');
  return response.data;
}

const notificationService = {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
};

export default notificationService;
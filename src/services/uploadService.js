import { mockApiResponse } from './api.js';

export function uploadMockFile(file) {
  const attachment = {
    id: `ATT-${Date.now()}`,
    name: file?.name || 'mock-attachment.txt',
    size: file?.size || 0,
    type: file?.type || 'application/octet-stream',
    status: 'uploaded',
    url: '#mock-upload',
  };

  return mockApiResponse(attachment, 300);
}

export function removeMockFile(attachmentId) {
  return mockApiResponse({ attachmentId, removed: true });
}

const uploadService = {
  uploadMockFile,
  removeMockFile,
};

export default uploadService;

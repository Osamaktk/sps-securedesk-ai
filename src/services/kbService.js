import axios from 'axios';
import { AI_URL } from '../config/constants.js';

const aiApi = axios.create({ baseURL: AI_URL });

async function listDocuments() {
  const response = await aiApi.get('/api/kb/documents');
  return response.data;
}

async function createDocument(filename, content) {
  const response = await aiApi.post('/api/kb/documents', { filename, content });
  return response.data;
}

async function updateDocument(filename, content) {
  const response = await aiApi.put(`/api/kb/documents/${encodeURIComponent(filename)}`, { content });
  return response.data;
}

async function deleteDocument(filename) {
  const response = await aiApi.delete(`/api/kb/documents/${encodeURIComponent(filename)}`);
  return response.data;
}

const kbService = { listDocuments, createDocument, updateDocument, deleteDocument };
export default kbService;
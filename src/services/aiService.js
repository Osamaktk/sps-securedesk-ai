import axios from 'axios';
import { AI_URL } from '../config/constants.js';

const aiApi = axios.create({
  baseURL: AI_URL,
});

export async function enhanceDescription(subject, description) {
  const response = await aiApi.post('/api/summarise', { subject, description });
  return response.data;
}

const aiService = {
  enhanceDescription,
};

export default aiService;
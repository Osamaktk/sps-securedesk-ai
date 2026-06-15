import { mockReports } from '../data/mockReports.js';
import { mockApiResponse } from './api.js';

export function getDashboardStats() {
  return mockApiResponse(mockReports.dashboardStats);
}

export function getReports() {
  return mockApiResponse(mockReports);
}

const reportService = {
  getDashboardStats,
  getReports,
};

export default reportService;

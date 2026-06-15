export const mockReports = {
  dashboardStats: {
    totalTickets: 12,
    openTickets: 9,
    resolvedTickets: 3,
    slaCompliance: 94.6,
    highRiskRequests: 3,
    averageResolutionHours: 6.8,
  },
  ticketsBySource: [
    { label: 'Email', value: 4, color: '#005BBB' },
    { label: 'Portal Form', value: 5, color: '#0B1F4D' },
    { label: 'Chat', value: 3, color: '#007BFF' },
  ],
  ticketsByCategory: [
    { label: 'Cloud', value: 2 },
    { label: 'Cybersecurity', value: 2 },
    { label: 'Identity and Access', value: 3 },
    { label: 'DevOps', value: 2 },
    { label: 'Internship/HR', value: 1 },
    { label: 'General IT', value: 2 },
  ],
  slaPerformance: [
    { period: 'Week 1', met: 92, breached: 8 },
    { period: 'Week 2', met: 95, breached: 5 },
    { period: 'Week 3', met: 94, breached: 6 },
    { period: 'Week 4', met: 97, breached: 3 },
  ],
  resolvedVsOpen: [
    { label: 'Open', value: 9 },
    { label: 'Resolved or Closed', value: 3 },
  ],
  highRiskAccessRequests: [
    {
      ticketId: 'SPS-2026-002',
      subject: 'Request privileged access to security analytics workspace',
      requesterName: 'Marcus Lee',
      status: 'Waiting Approval',
      ageHours: 2.3,
    },
    {
      ticketId: 'SPS-2026-003',
      subject: 'Suspicious sign-in alert after international travel',
      requesterName: 'Elena Petrov',
      status: 'In Progress',
      ageHours: 1.4,
    },
    {
      ticketId: 'SPS-2026-010',
      subject: 'Repository secret detected in recent commit',
      requesterName: 'Ethan Brown',
      status: 'In Progress',
      ageHours: 0.7,
    },
  ],
};

export default mockReports;

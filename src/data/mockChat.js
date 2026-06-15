export const mockChatMessages = [
  {
    id: 'MSG-001',
    role: 'assistant',
    type: 'message',
    content:
      'Hi, I’m SecureDesk AI. I can help with VPN, email, laptop, cloud, phishing, access policy, and intern onboarding questions.',
    createdAt: '2026-06-09T09:00:00Z',
  },
  {
    id: 'MSG-002',
    role: 'user',
    type: 'message',
    content: 'How do I request temporary access to the security analytics workspace?',
    createdAt: '2026-06-09T09:01:00Z',
  },
  {
    id: 'MSG-003',
    role: 'assistant',
    type: 'message',
    content:
      'Submit a privileged access request with the workspace name, business reason, requested duration, and manager approval. Security review is required before access is granted.',
    citations: [
      {
        id: 'CIT-001',
        type: 'citation_chip',
        label: 'KB-1042 Privileged Access Requests',
        source: 'Knowledge Base',
      },
    ],
    createdAt: '2026-06-09T09:01:04Z',
  },
  {
    id: 'MSG-004',
    role: 'user',
    type: 'message',
    content: 'This is urgent and I cannot wait for the standard workflow.',
    createdAt: '2026-06-09T09:02:00Z',
  },
  {
    id: 'MSG-005',
    role: 'assistant',
    type: 'escalation',
    content:
      'Because this request involves urgent privileged access, I recommend escalation to Identity Governance and Security Operations. I can create a ticket with this conversation summary.',
    escalation: {
      recommended: true,
      reason: 'Urgent privileged access request',
      suggestedPriority: 'High',
      suggestedRisk: 'High Risk',
    },
    createdAt: '2026-06-09T09:02:03Z',
  },
];

export const mockChatResponses = {
  default: {
    content:
      'I found general guidance, but an agent may need more details before taking action.',
    citations: [
      {
        id: 'CIT-DEFAULT',
        type: 'citation_chip',
        label: 'SPS Support Guide',
        source: 'Knowledge Base',
      },
    ],
  },
  password: {
    content:
      'Use the approved self-service password reset page. If multi-factor authentication is unavailable, I can prepare an identity support ticket.',
    citations: [
      {
        id: 'CIT-PASSWORD',
        type: 'citation_chip',
        label: 'KB-1003 Password Reset',
        source: 'Knowledge Base',
      },
    ],
  },
  vpn: {
    content:
      'Confirm your internet connection, reconnect the corporate VPN client, and capture the error time. Persistent production VPN failures should be escalated to Cloud Operations.',
    citations: [
      {
        id: 'CIT-VPN',
        type: 'citation_chip',
        label: 'VPN Policy',
        source: 'Knowledge Base',
      },
    ],
  },
  phishing: {
    content:
      'Do not open links or attachments. Use the approved phishing-report action in your email client, then notify Security Operations if credentials were entered.',
    citations: [
      {
        id: 'CIT-PHISHING',
        type: 'citation_chip',
        label: 'Phishing Response Policy',
        source: 'Knowledge Base',
      },
    ],
  },
  cloud: {
    content:
      'Check the VM power state, recent deployment activity, and platform health. Production or repeated failures should be escalated to Cloud Operations.',
    citations: [
      {
        id: 'CIT-CLOUD',
        type: 'citation_chip',
        label: 'Cloud Operations Guide',
        source: 'Knowledge Base',
      },
    ],
  },
  access: {
    content:
      'Access requests require a business reason, requested duration, and manager approval. Privileged access also requires a security review.',
    citations: [
      {
        id: 'CIT-ACCESS',
        type: 'citation_chip',
        label: 'Access Policy',
        source: 'Knowledge Base',
      },
    ],
  },
  onboarding: {
    content:
      'Intern onboarding access is provisioned after the HR record, manager assignment, and start date are confirmed.',
    citations: [
      {
        id: 'CIT-ONBOARDING',
        type: 'citation_chip',
        label: 'Intern Onboarding',
        source: 'Knowledge Base',
      },
    ],
  },
};

export default mockChatMessages;

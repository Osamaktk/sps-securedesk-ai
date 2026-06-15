import { useEffect, useRef, useState } from 'react';
import ChatInput from '../../components/chat/ChatInput';
import ChatMessage from '../../components/chat/ChatMessage';
import ChatSuggestions from '../../components/chat/ChatSuggestions';
import CreateTicketFromChat from '../../components/chat/CreateTicketFromChat';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import {
  createMockTicketFromChat,
  getInitialMessages,
  sendMockMessage,
} from '../../services/chatService.js';

const knowledgeTopics = [
  'VPN',
  'Email',
  'Laptop',
  'Cloud Checklist',
  'Phishing',
  'Intern Onboarding',
  'Access Policy',
  'Product Overviews',
];

const initialTicketDraft = {
  subject: 'Helpdesk assistance requested from SecureDesk AI',
  summary:
    'The requester needs additional help after reviewing approved knowledge-base guidance.',
  category: 'General IT',
  priority: 'Medium',
  risk: 'Normal',
  source: 'chat',
};

const escalationTerms = [
  'create ticket',
  'report phishing',
  'cannot resolve',
  "can't resolve",
  'human agent',
  'speak to an agent',
];

function shouldShowEscalation(message, response) {
  const normalized = message.toLowerCase();
  return (
    escalationTerms.some((term) => normalized.includes(term)) ||
    response.content.includes('agent may need more details')
  );
}

function createUserMessage(content) {
  return {
    id: `PAGE-USER-${Date.now()}`,
    role: 'user',
    type: 'message',
    content,
    createdAt: new Date().toISOString(),
  };
}

export default function AIChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showEscalation, setShowEscalation] = useState(false);
  const [ticketDraft, setTicketDraft] = useState(initialTicketDraft);
  const [ticketConfirmation, setTicketConfirmation] = useState('');
  const conversationRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    getInitialMessages().then((initialMessages) => {
      if (!isMounted) return;
      setMessages(initialMessages.slice(0, 3));
      setIsLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const conversation = conversationRef.current;
    if (conversation) conversation.scrollTop = conversation.scrollHeight;
  }, [isLoading, messages, showEscalation]);

  const handleSend = async (content) => {
    if (content.toLowerCase() === 'create ticket') {
      setShowEscalation(true);
      return;
    }

    setMessages((current) => [...current, createUserMessage(content)]);
    setIsLoading(true);

    const response = await sendMockMessage(content);
    setMessages((current) => [...current, response]);
    setIsLoading(false);

    setTicketDraft((current) => ({
      ...current,
      subject: `${content.slice(0, 68)}${content.length > 68 ? '...' : ''}`,
      summary: `SecureDesk AI reviewed the request: ${content}`,
      category:
        content.toLowerCase().includes('cloud') ||
        content.toLowerCase().includes('vm')
          ? 'Cloud'
          : content.toLowerCase().includes('access')
            ? 'Identity and Access'
            : content.toLowerCase().includes('phish')
              ? 'Cybersecurity'
              : 'General IT',
      priority: content.toLowerCase().includes('phish') ? 'High' : 'Medium',
      risk: content.toLowerCase().includes('phish') ? 'Elevated' : 'Normal',
    }));

    if (shouldShowEscalation(content, response)) setShowEscalation(true);
  };

  const handleCreateTicket = async (draft = ticketDraft) => {
    await createMockTicketFromChat({
      ...draft,
      aiSummary: draft.summary,
    });
    setTicketConfirmation('Ticket SPS-2026-042 created successfully.');
  };

  return (
    <section className="page ai-chat-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">AI-assisted support</p>
          <h1>SecureDesk AI Assistant</h1>
          <p>
            Ask helpdesk questions using approved SPS knowledge or prepare a
            support ticket for human review.
          </p>
        </div>
        <Badge tone="blue">Mock knowledge base</Badge>
      </div>

      <div className="ai-chat-layout">
        <section className="ai-chat-conversation-card" aria-label="AI conversation">
          <div className="ai-chat-conversation-card__header">
            <div className="ai-chat-conversation-card__identity">
              <span aria-hidden="true">AI</span>
              <div>
                <strong>SPS SecureDesk AI</strong>
                <small>Knowledge-base assistant</small>
              </div>
            </div>
            <Badge tone="green">Available</Badge>
          </div>

          <div className="ai-chat-conversation" ref={conversationRef}>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="chat-typing" aria-label="SecureDesk AI is responding">
                <span />
                <span />
                <span />
              </div>
            )}
            {showEscalation && (
              <CreateTicketFromChat
                draft={ticketDraft}
                onContinue={() => setShowEscalation(false)}
                onCreate={handleCreateTicket}
                onCreated={() =>
                  setTicketConfirmation('Ticket SPS-2026-042 created successfully.')
                }
              />
            )}
          </div>

          <div className="ai-chat-composer">
            <ChatSuggestions disabled={isLoading} onSelect={handleSend} />
            <ChatInput disabled={isLoading} onSend={handleSend} />
            <p className="chat-safety-footer">
              AI can suggest answers, but sensitive actions require human approval.
            </p>
          </div>
        </section>

        <aside className="ai-chat-side-panel">
          <Card
            className="ai-chat-preview-card"
            title="Ticket Preview"
            subtitle="Prepared from the current mock conversation."
            actions={<Badge value="chat" />}
          >
            <dl className="ai-chat-ticket-preview">
              <div>
                <dt>Suggested subject</dt>
                <dd>{ticketDraft.subject}</dd>
              </div>
              <div>
                <dt>Suggested category</dt>
                <dd>{ticketDraft.category}</dd>
              </div>
              <div className="ai-chat-ticket-preview__badges">
                <span>
                  <dt>Priority</dt>
                  <dd>
                    <Badge value={ticketDraft.priority.toLowerCase()} />
                  </dd>
                </span>
                <span>
                  <dt>Risk level</dt>
                  <dd>
                    <Badge
                      tone={ticketDraft.risk === 'Elevated' ? 'amber' : 'green'}
                    >
                      {ticketDraft.risk}
                    </Badge>
                  </dd>
                </span>
                <span>
                  <dt>Source</dt>
                  <dd>
                    <Badge value="chat" />
                  </dd>
                </span>
              </div>
            </dl>
            <Button
              className="ai-chat-ticket-preview__button"
              onClick={() => handleCreateTicket(ticketDraft)}
            >
              Create Ticket
            </Button>
            {ticketConfirmation && (
              <p className="ai-chat-ticket-confirmation" role="status">
                {ticketConfirmation}
              </p>
            )}
          </Card>

          <Card
            className="ai-chat-topics-card"
            title="Knowledge Base Topics"
            subtitle="Start with an approved support topic."
          >
            <div className="ai-chat-topics">
              {knowledgeTopics.map((topic) => (
                <button
                  type="button"
                  disabled={isLoading}
                  key={topic}
                  onClick={() => handleSend(topic)}
                >
                  <span aria-hidden="true">{topic.slice(0, 2).toUpperCase()}</span>
                  {topic}
                </button>
              ))}
            </div>
          </Card>

          <div className="ai-chat-safety-note">
            <span aria-hidden="true">!</span>
            <p>
              SecureDesk AI answers from the approved knowledge base only.
              Sensitive requests require human approval.
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}

import { useEffect, useRef, useState } from 'react';
import { createMockTicketFromChat, getInitialMessages, sendMockMessage } from '../../services/chatService.js';
import ChatHeader from './ChatHeader';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import ChatSuggestions from './ChatSuggestions';
import CreateTicketFromChat from './CreateTicketFromChat';

const escalationTerms = [
  'create ticket',
  'report phishing',
  'cannot resolve',
  "can't resolve",
  'human agent',
  'speak to an agent',
];

function shouldShowEscalation(message) {
  const normalized = message.toLowerCase();
  return escalationTerms.some((term) => normalized.includes(term));
}

export default function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showTicketCard, setShowTicketCard] = useState(false);
  const messageAreaRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    getInitialMessages().then((initialMessages) => {
      if (!isMounted) return;
      setMessages(initialMessages.slice(0, 1));
      setIsLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const messageArea = messageAreaRef.current;
    if (messageArea) messageArea.scrollTop = messageArea.scrollHeight;
  }, [messages, showTicketCard, isLoading]);

  const handleSend = async (content) => {
    if (content.toLowerCase() === 'create ticket') {
      setShowTicketCard(true);
      return;
    }

    const userMessage = {
      id: `USER-${Date.now()}`,
      role: 'user',
      type: 'message',
      content,
      createdAt: new Date().toISOString(),
    };

    setMessages((current) => [...current, userMessage]);
    setIsLoading(true);

    const response = await sendMockMessage(content);
    setMessages((current) => [...current, response]);
    setIsLoading(false);

    if (
      shouldShowEscalation(content) ||
      response.content.includes('agent may need more details')
    ) {
      setShowTicketCard(true);
    }
  };

  const handleCreateTicket = (ticketDraft) =>
    createMockTicketFromChat({
      ...ticketDraft,
      aiSummary: ticketDraft.summary,
    });

  return (
    <section
      className="chat-window"
      aria-label="SPS SecureDesk AI chat"
      aria-live="polite"
    >
      <ChatHeader onClose={onClose} />

      <div className="chat-window__messages" ref={messageAreaRef}>
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
        {showTicketCard && (
          <CreateTicketFromChat
            onContinue={() => setShowTicketCard(false)}
            onCreate={handleCreateTicket}
          />
        )}
      </div>

      <div className="chat-window__composer">
        <ChatSuggestions disabled={isLoading} onSelect={handleSend} />
        <ChatInput disabled={isLoading} onSend={handleSend} />
        <p className="chat-safety-footer">
          AI can suggest answers, but sensitive actions require human approval.
        </p>
      </div>
    </section>
  );
}

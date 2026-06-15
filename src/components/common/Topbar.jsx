import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import SearchInput from './SearchInput';

const pageTitles = {
  '/requester': 'Dashboard',
  '/requester/submit': 'Submit Request',
  '/requester/tickets': 'My Tickets',
  '/requester/ai-chat': 'AI Chat',
  '/agent': 'Agent Dashboard',
  '/agent/queue': 'Ticket Queue',
  '/security': 'Security Dashboard',
  '/security/approvals': 'Approvals',
  '/manager': 'Manager Dashboard',
  '/manager/reports': 'Reports',
  '/admin': 'Admin Settings',
  '/admin/users': 'Users',
  '/admin/knowledge-base': 'Knowledge Base',
  '/admin/categories': 'Categories',
  '/admin/sla-settings': 'SLA Settings',
  '/admin/email-settings': 'Email Settings',
};

function getPageTitle(pathname) {
  if (pathname.startsWith('/agent/tickets/')) return 'Ticket Detail';
  return pageTitles[pathname] || 'SecureDesk AI';
}

export default function Topbar({ onOpenMenu }) {
  const { pathname } = useLocation();
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  return (
    <header className="topbar">
      <button
        className="icon-button menu-button"
        type="button"
        aria-label="Open navigation"
        onClick={onOpenMenu}
      >
        Menu
      </button>

      <div className="topbar__context">
        <span className="topbar__label">SPS SecureDesk AI</span>
        <strong>{getPageTitle(pathname)}</strong>
      </div>

      <div className="topbar__search">
        <SearchInput
          aria-label="Search helpdesk"
          placeholder="Search tickets, users, or articles"
        />
      </div>

      <div className="topbar__actions">
        <button
          className="notification-button"
          type="button"
          aria-label="Notifications, 3 unread"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M14 21h-4" />
          </svg>
          <span className="notification-button__count">3</span>
        </button>

        <div className="profile-menu">
          <button
            className="profile-menu__trigger"
            type="button"
            aria-label="Open user profile menu"
            aria-expanded={isProfileOpen}
            aria-haspopup="menu"
            onClick={() => setIsProfileOpen((value) => !value)}
          >
            <span className="user-avatar" aria-hidden="true">
              SD
            </span>
            <span className="profile-menu__copy">
              <strong>Service Desk User</strong>
              <span>Operations</span>
            </span>
            <span className="profile-menu__chevron" aria-hidden="true">
              v
            </span>
          </button>

          {isProfileOpen && (
            <div className="profile-menu__dropdown" role="menu">
              <button type="button" role="menuitem">
                Profile settings
              </button>
              <button type="button" role="menuitem">
                Help &amp; support
              </button>
              <button type="button" role="menuitem">
                Sign out placeholder
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

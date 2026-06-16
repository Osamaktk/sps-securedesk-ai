import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import ChatLauncher from '../chat/ChatLauncher';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function AppShell() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') setIsMenuOpen(false);
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (!isMenuOpen) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [isMenuOpen]);

  return (
    <div
      className={`app-shell ${
        isSidebarCollapsed ? 'app-shell--sidebar-collapsed' : ''
      }`}
    >
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        onToggleCollapse={() => setIsSidebarCollapsed((value) => !value)}
      />

      {isMenuOpen && (
        <button
          className="sidebar-backdrop"
          type="button"
          aria-label="Close navigation"
          onClick={() => setIsMenuOpen(false)}
        />
      )}

      <div className="workspace">
        <Topbar onOpenMenu={() => setIsMenuOpen(true)} />

        <main className="workspace__content" id="main-content" tabIndex="-1">
          <Outlet />
        </main>
      </div>

      <ChatLauncher />
    </div>
  );
}

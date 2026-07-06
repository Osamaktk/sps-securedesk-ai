import { createContext, useContext, useEffect, useState } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const syncUserFromStorage = () => {
      const currentUser = authService.getCurrentUser();
      setUser(currentUser);
      setLoading(false);
    };

    const handleLogout = () => {
      setUser(null);
      setLoading(false);
    };

    syncUserFromStorage();
    window.addEventListener('auth-login', syncUserFromStorage);
    window.addEventListener('auth-logout', handleLogout);
    return () => {
      window.removeEventListener('auth-login', syncUserFromStorage);
      window.removeEventListener('auth-logout', handleLogout);
    };
  }, []);

  const login = async (email, password) => {
    const loggedInUser = await authService.login(email, password);
    setUser(loggedInUser);
    return loggedInUser;
  };

  const logout = (navigate) => {
    authService.logout(navigate);
    setUser(null);
    setLoading(false);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

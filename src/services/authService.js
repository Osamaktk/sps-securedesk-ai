import api from './api.js';

async function login(email, password) {
  const response = await api.post('/auth/login', { email, password });
  const { access_token, user } = response.data;
  sessionStorage.setItem('token', access_token);
  sessionStorage.setItem('user', JSON.stringify(user));
  window.dispatchEvent(new Event('auth-login'));
  return user;
}

async function register(email, full_name, password, role) {
  const response = await api.post('/auth/register', {
    email,
    full_name,
    password,
    role,
  });
  return response.data;
}

function logout(navigate) {
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('user');
  window.dispatchEvent(new Event('auth-logout'));
  if (navigate) {
    navigate('/login', { replace: true });
  }
}

function getCurrentUser() {
  const user = sessionStorage.getItem('user');
  if (!user) return null;

  try {
    return JSON.parse(user);
  } catch (error) {
    console.error('[authService] Invalid session user payload:', error);
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    return null;
  }
}

function isLoggedIn() {
  return !!sessionStorage.getItem('token');
}

const authService = {
  login,
  register,
  logout,
  getCurrentUser,
  isLoggedIn,
};

export default authService;

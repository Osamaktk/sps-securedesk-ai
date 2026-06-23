import api from './api.js';

export async function getUsers() {
  const response = await api.get('/users');
  return response.data;
}

export async function getUser(id) {
  const response = await api.get(`/users/${id}`);
  return response.data;
}

export async function createUser(data) {
  const response = await api.post('/users', {
    email: data.email,
    full_name: data.full_name,
    password: data.password,
    role: data.role,
    is_active: data.is_active ?? true,
  });
  return response.data;
}

export async function updateUser(id, data) {
  const response = await api.patch(`/users/${id}`, {
    full_name: data.full_name,
    role: data.role,
    is_active: data.is_active,
  });
  return response.data;
}

export async function deleteUser(id) {
  await api.delete(`/users/${id}`);
}

export async function getRoles() {
  const response = await api.get('/users/roles');
  return response.data;
}

const userService = {
  getUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
  getRoles,
};

export default userService;
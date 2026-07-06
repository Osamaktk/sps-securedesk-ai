import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AsyncState from './AsyncState';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <AsyncState title="Loading" description="Checking authentication..." />;
  }

  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/unauthorized" replace />;
  return children;
};

export default ProtectedRoute;
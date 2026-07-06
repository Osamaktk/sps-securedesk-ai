import { Link } from 'react-router-dom';
import AsyncState from '../components/common/AsyncState';

export default function NotFound() {
  return (
    <AsyncState
      type="error"
      title="Page not found"
      description="The requested SecureDesk AI page does not exist."
    >
      <Link className="button button--primary" to="/requester">
        Return to dashboard
      </Link>
    </AsyncState>
  );
}

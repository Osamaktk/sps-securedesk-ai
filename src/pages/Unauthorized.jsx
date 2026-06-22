import { Link } from 'react-router-dom';
import AsyncState from '../components/common/AsyncState';

export default function Unauthorized() {
  return (
    <AsyncState
      type="error"
      title="Access unavailable"
      description="Your current role does not have access to this SecureDesk AI page."
    >
      <Link className="button button--primary" to="/">
        Return to workspace
      </Link>
    </AsyncState>
  );
}

import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';

const EMAIL_CHANNELS = [
  {
    id: 'MAIL-01',
    setting: 'Inbound support mailbox',
    description: 'IMAP polling — converts incoming emails to tickets',
    direction: 'Inbound',
    configKey: 'IMAP_HOST / IMAP_USER',
  },
  {
    id: 'MAIL-02',
    setting: 'Outbound notifications',
    description: 'SMTP delivery for ticket acknowledgements and status updates',
    direction: 'Outbound',
    configKey: 'SMTP_HOST / SMTP_PORT',
  },
  {
    id: 'MAIL-03',
    setting: 'Approval alerts',
    description: 'High-risk ticket notifications sent to the security team',
    direction: 'Outbound',
    configKey: 'EMAIL_FROM_ADDRESS',
  },
];

export default function EmailSettings() {
  return (
    <section className="page admin-management-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">System administration</p>
          <h1>Email Settings</h1>
          <p>Inbound and outbound email channels managed by the email_worker service.</p>
        </div>
      </div>

      <div className="future-integration-note">
        <span aria-hidden="true">ENV</span>
        <div>
          <strong>Environment-based configuration</strong>
          <p>
            Email settings are configured via <code>email_worker/.env</code> and docker-compose environment variables.
            Update <code>IMAP_HOST</code>, <code>IMAP_USER</code>, <code>SMTP_HOST</code>, and related keys to change channel configuration.
          </p>
        </div>
      </div>

      <Card
        className="admin-management-card"
        title="Email channel status"
        subtitle="Active channels handled by the email_worker service."
        actions={<Badge tone="blue">{EMAIL_CHANNELS.length} channels</Badge>}
      >
        <div className="admin-management-table-wrap">
          <table className="admin-management-table">
            <caption className="visually-hidden">Email channel configuration</caption>
            <thead>
              <tr>
                <th scope="col">Channel</th>
                <th scope="col">Description</th>
                <th scope="col">Direction</th>
                <th scope="col">Config Key</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {EMAIL_CHANNELS.map((channel) => (
                <tr key={channel.id}>
                  <td>{channel.setting}</td>
                  <td>{channel.description}</td>
                  <td>{channel.direction}</td>
                  <td><code>{channel.configKey}</code></td>
                  <td><Badge tone="blue">Active</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </section>
  );
}
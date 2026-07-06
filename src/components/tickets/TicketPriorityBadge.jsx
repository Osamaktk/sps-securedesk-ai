import Badge from '../common/Badge';

export default function TicketPriorityBadge({ priority }) {
  return <Badge value={String(priority).toLowerCase()}>{priority}</Badge>;
}

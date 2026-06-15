import PagePlaceholder from './PagePlaceholder';
import { pageMeta } from '../../data/pageMeta';

export function createPlaceholderPage(pageKey) {
  return function PlaceholderPage() {
    return <PagePlaceholder {...pageMeta[pageKey]} />;
  };
}

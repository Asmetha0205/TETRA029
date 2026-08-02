export function formatPercentage(value: number): string {
  if (isNaN(value)) return '0%';
  return `${Math.round(value * 100) / 100}%`;
}

export function formatScoreColor(score: number): {
  text: string;
  bg: string;
  border: string;
  badge: string;
} {
  if (score >= 80) {
    return {
      text: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      badge: 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400',
    };
  } else if (score >= 60) {
    return {
      text: 'text-amber-500',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      badge: 'bg-amber-500/20 text-amber-600 dark:text-amber-400',
    };
  } else {
    return {
      text: 'text-rose-500',
      bg: 'bg-rose-500/10',
      border: 'border-rose-500/30',
      badge: 'bg-rose-500/20 text-rose-600 dark:text-rose-400',
    };
  }
}

export function formatPriorityBadge(priority: string) {
  switch (priority?.toUpperCase()) {
    case 'CRITICAL':
      return { label: 'CRITICAL', color: 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30' };
    case 'HIGH':
      return { label: 'HIGH', color: 'bg-orange-500/15 text-orange-600 dark:text-orange-400 border-orange-500/30' };
    case 'MEDIUM':
      return { label: 'MEDIUM', color: 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30' };
    case 'LOW':
      return { label: 'LOW', color: 'bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30' };
    default:
      return { label: priority || 'MEDIUM', color: 'bg-gray-500/15 text-gray-600 dark:text-gray-400 border-gray-500/30' };
  }
}

export function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

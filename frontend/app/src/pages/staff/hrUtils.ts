export type HrStatus = 'idle' | 'submitting' | 'success' | 'error';

export function formatRange(startDate: string | undefined, endDate: string | undefined) {
  if (!startDate && !endDate) {
    return 'Даты не указаны';
  }
  const start = startDate ? new Date(startDate).toLocaleDateString('ru-RU') : '—';
  const end = endDate ? new Date(endDate).toLocaleDateString('ru-RU') : '—';
  return `${start} — ${end}`;
}

export function formatStatus(status?: string) {
  if (!status) {
    return 'Неизвестно';
  }
  const normalized = status.toLowerCase();
  switch (normalized) {
    case 'approved':
      return 'Одобрено';
    case 'pending':
      return 'На рассмотрении';
    case 'rejected':
      return 'Отклонено';
    case 'submitted':
      return 'Отправлено';
    default:
      return status;
  }
}

export function normalizeTimeInput(value: string) {
  if (!value) {
    return value;
  }
  return value.length === 5 && value.includes(':') ? `${value}:00` : value;
}


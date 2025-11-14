import { apiFetch } from './httpClient';

export interface EventAgendaItem {
  time?: string;
  title?: string;
  description?: string;
}

export interface EventLinks {
  landing?: string;
  tickets?: string;
  stream?: string;
}

export interface Event {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  category?: string;
  cover?: string;
  location?: string;
  organizer?: string;
  starts_at?: string;
  ends_at?: string;
  registration_deadline?: string;
  registration_required?: boolean;
  remaining?: number;
  capacity?: number;
  status?: string;
  visibility?: string;
  tags?: string[];
  agenda?: EventAgendaItem[];
  links?: EventLinks;
  meta?: Record<string, unknown>;
}

type ApiResponse<T> = { data?: T };
type ApiListResponse<T> = { data?: T[] };
type ApiSingleResponse<T> = { data?: T };
type ApiPaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

export async function getEvents(params?: {
  q?: string;
  category?: string;
}): Promise<Event[]> {
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.append('q', params.q);
  if (params?.category) queryParams.append('category', params.category);

  const path = `/events${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  const response = await apiFetch<Event[] | ApiListResponse<Event> | ApiPaginatedResponse<Event>>(path);
  
  // Проверяем разные форматы ответа
  if (Array.isArray(response)) {
    return response;
  }
  
  // Пагинированный ответ с results
  if (response && typeof response === 'object' && 'results' in response) {
    return (response as ApiPaginatedResponse<Event>).results ?? [];
  }
  
  // Ответ с data
  if (response && typeof response === 'object' && 'data' in response) {
    return (response as ApiListResponse<Event>).data ?? [];
  }
  
  return [];
}

export async function getEventById(id: string): Promise<Event | null> {
  const response = await apiFetch<Event | ApiSingleResponse<Event>>(`/events/${id}`);
  
  if ('id' in (response ?? {})) {
    return response as Event;
  }
  return (response as ApiSingleResponse<Event>)?.data ?? null;
}

export async function submitEventRegistration({
  eventId,
  formPayload,
}: {
  eventId: string;
  formPayload?: Record<string, unknown>;
}): Promise<{ success: boolean }> {
  await apiFetch(`/events/${eventId}/registrations`, {
    method: 'POST',
    body: {
      event_id: eventId,
      form_payload: formPayload ?? {},
    },
  });
  return { success: true };
}



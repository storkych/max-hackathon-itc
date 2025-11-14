import { apiFetch } from './httpClient';

export interface DormitoryApplication {
  id: string;
  status?: string;
  room?: string;
  building?: string;
  submittedAt?: string;
}

type ApiResponse<T> = { data?: T };
type ApiListResponse<T> = { data?: T[] };

export async function getDormitoryApplications(): Promise<DormitoryApplication[]> {
  // Получаем заявки на поддержку (support tickets)
  const response = await apiFetch<DormitoryApplication[] | ApiListResponse<DormitoryApplication>>('/dorm/support/tickets/my');
  
  if (Array.isArray(response)) {
    return response;
  }
  return response?.data ?? [];
}

export async function submitDormitoryRequest(payload: {
  preferredRoom?: string;
  preferredBuilding?: string;
  reason?: string;
  consents?: { personal_data: boolean };
}): Promise<{ success: boolean; applicationId?: string }> {
  // Создаём тикет в службе поддержки
  const response = await apiFetch<ApiResponse<{ ticket_id?: string; id?: string }>>('/dorm/support/tickets', {
    method: 'POST',
    body: {
      subject: 'Заявка на общежитие',
      description: payload.reason || '',
      preferred_room: payload.preferredRoom,
      preferred_building: payload.preferredBuilding,
      ...payload.consents,
    } as Record<string, unknown>,
  });
  return {
    success: true,
    applicationId: response?.data?.ticket_id ?? response?.data?.id,
  };
}



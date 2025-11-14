import { apiFetch } from './httpClient';

export interface DeaneryRequest {
  id: string;
  type?: string;
  status?: string;
  submittedAt?: string;
  response?: string;
}

export interface DeaneryRequestPayload {
  type: string;
  description?: string;
  language?: string;
  attachments?: Array<{ name: string; url: string }>;
  consents?: { personal_data: boolean };
  [key: string]: unknown;
}

type ApiResponse<T> = { data?: T };
type ApiListResponse<T> = { data?: T[] };

export async function getDeaneryRequests(): Promise<DeaneryRequest[]> {
  // Получаем все типы запросов: справки, академические отпуска
  const [certificates, academicLeaves] = await Promise.all([
    apiFetch<DeaneryRequest[] | ApiListResponse<DeaneryRequest>>('/deanery/certificates/my').catch(() => []),
    apiFetch<DeaneryRequest[] | ApiListResponse<DeaneryRequest>>('/deanery/academic-leave/my').catch(() => []),
  ]);

  const allRequests: DeaneryRequest[] = [];
  
  if (Array.isArray(certificates)) {
    allRequests.push(...certificates);
  } else if (certificates && 'data' in certificates) {
    allRequests.push(...(certificates.data ?? []));
  }
  
  if (Array.isArray(academicLeaves)) {
    allRequests.push(...academicLeaves);
  } else if (academicLeaves && 'data' in academicLeaves) {
    allRequests.push(...(academicLeaves.data ?? []));
  }

  return allRequests;
}

export async function submitDeaneryRequest(payload: DeaneryRequestPayload): Promise<{ success: boolean; requestId?: string }> {
  // В зависимости от типа запроса используем разные endpoints
  let endpoint = '/deanery/certificates';
  if (payload.type === 'academic-leave' || payload.type === 'academic_leave') {
    endpoint = '/deanery/academic-leave';
  } else if (payload.type === 'compensation') {
    endpoint = '/deanery/compensations';
  } else if (payload.type === 'transfer') {
    endpoint = '/deanery/transfer-requests';
  }

  const response = await apiFetch<ApiResponse<{ request_id?: string; id?: string }>>(endpoint, {
    method: 'POST',
    body: payload as Record<string, unknown>,
  });
  return {
    success: true,
    requestId: response?.data?.request_id ?? response?.data?.id,
  };
}



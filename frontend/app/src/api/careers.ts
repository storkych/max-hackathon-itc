import { apiFetch } from './httpClient';

export interface Vacancy {
  id: string;
  title: string;
  company: {
    id?: string;
    name: string;
    verified_partner?: boolean;
    logo_url?: string;
    site_url?: string;
  } | string; // Поддержка и объекта, и строки для обратной совместимости
  location: {
    city?: string;
    country?: string;
    type?: string;
  } | string; // Поддержка и объекта, и строки
  direction: string | string[];
  grade: string;
  description?: string;
  requirements?: string[] | {
    tools?: string[];
    portfolio?: boolean;
  };
  remote?: boolean;
  salary?: {
    from?: number;
    to?: number;
    currency?: string;
    gross?: boolean;
  };
  employment?: string;
  experience_min_years?: number;
  skills?: string[];
  benefits?: string[];
  posted_at?: string;
  published_until?: string;
}

export interface CareerConsultation {
  id: string;
  topic: string;
  subtopic?: string;
  mentor?: string;
  status: 'scheduled' | 'completed' | 'cancelled';
  slot?: string;
  channel?: string;
}

type ApiResponse<T> = { data?: T };
type ApiListResponse<T> = { data?: T[] };
type ApiPaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

export async function getVacancies(params?: {
  q?: string;
  direction?: string;
  grade?: string;
  remote_only?: boolean;
}): Promise<Vacancy[]> {
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.append('q', params.q);
  if (params?.direction) queryParams.append('direction', params.direction);
  if (params?.grade) queryParams.append('grade', params.grade);
  if (params?.remote_only) queryParams.append('remote_only', 'true');

  const path = `/careers/vacancies${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  const response = await apiFetch<Vacancy[] | ApiListResponse<Vacancy> | ApiPaginatedResponse<Vacancy>>(path);
  
  // Проверяем разные форматы ответа
  if (Array.isArray(response)) {
    return response;
  }
  
  // Пагинированный ответ с results
  if (response && typeof response === 'object' && 'results' in response) {
    return (response as ApiPaginatedResponse<Vacancy>).results ?? [];
  }
  
  // Ответ с data
  if (response && typeof response === 'object' && 'data' in response) {
    return (response as ApiListResponse<Vacancy>).data ?? [];
  }
  
  return [];
}

type ApiSingleResponse<T> = { data?: T };

export async function getVacancyById(id: string): Promise<Vacancy | null> {
  const response = await apiFetch<Vacancy | ApiSingleResponse<Vacancy>>(`/careers/vacancies/${id}`);
  
  if ('id' in (response ?? {})) {
    return response as Vacancy;
  }
  return (response as ApiSingleResponse<Vacancy>)?.data ?? null;
}

export async function submitVacancyApplication(payload: {
  vacancyId: string;
  roleCode?: string;
  motivation?: string;
  attachments?: Array<{ name: string; url: string }>;
  cvUrl?: string;
  portfolioUrl?: string;
  consents?: { personal_data: boolean };
}): Promise<{ success: boolean; applicationId?: string }> {
  const response = await apiFetch<ApiResponse<{ application_id: string }>>(
    `/careers/vacancies/${payload.vacancyId}/apply`,
    {
      method: 'POST',
      body: payload as Record<string, unknown>,
    }
  );
  return {
    success: true,
    applicationId: response?.data?.application_id,
  };
}

export async function getCareerConsultations(): Promise<CareerConsultation[]> {
  const response = await apiFetch<CareerConsultation[] | ApiListResponse<CareerConsultation>>('/careers/consultations/my');
  
  if (Array.isArray(response)) {
    return response;
  }
  return response?.data ?? [];
}

export async function submitCareerConsultationRequest(payload: {
  topic: string;
  subtopic?: string;
  preferred_slots?: string;
}): Promise<{ success: boolean; consultationId?: string }> {
  const response = await apiFetch<ApiResponse<{ consultation_id: string }>>('/careers/consultations', {
    method: 'POST',
    body: payload as Record<string, unknown>,
  });
  return {
    success: true,
    consultationId: response?.data?.consultation_id,
  };
}


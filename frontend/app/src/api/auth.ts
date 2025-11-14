import { apiFetch } from './httpClient';

export interface CurrentUser {
  id: string;
  email?: string;
  fullName?: string;
  roles?: string[];
  role?: string;
}

type ApiResponse<T> = { data?: T };

export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  const response = await apiFetch<ApiResponse<any> | { user?: any }>('/auth/me');
  if (!response) {
    return null;
  }

  // API может вернуть { data: {...} }, { user: {...} } или просто объект пользователя
  const data = (response as any).data ?? (response as any).user ?? response;
  if (!data) {
    return null;
  }

  return {
    id: data.id ?? data.user_id ?? 'unknown',
    email: data.email ?? data.login ?? undefined,
    fullName: data.full_name ?? data.fullName ?? data.name ?? undefined,
    roles: Array.isArray(data.roles) ? data.roles : undefined,
    role: data.role ?? undefined,
  };
}

export async function logout(): Promise<void> {
  try {
    await apiFetch('/auth/logout', {
      method: 'POST',
    });
  } catch (error) {
    console.error('Logout error', error);
    // Продолжаем выход даже если запрос не удался
  } finally {
    // Очищаем токен из localStorage
    try {
      localStorage.removeItem('access_token');
      localStorage.removeItem('api_access_token');
    } catch (err) {
      console.warn('Failed to clear tokens from localStorage', err);
    }
  }
}

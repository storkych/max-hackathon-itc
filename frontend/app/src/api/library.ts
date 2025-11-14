import { apiFetch } from './httpClient';

export interface LibraryBook {
  id: string;
  title: string;
  subtitle?: string;
  authors?: string[];
  publisher?: string;
  published_year?: number;
  isbn?: string;
  language?: string;
  description?: string;
  cover_url?: string;
  media_type?: string;
  formats?: string[];
  tags?: string[];
  categories?: string[];
  availability?: {
    in_stock?: number;
    total?: number;
    queue?: number;
  };
  rating?: {
    value?: number;
    votes?: number;
  };
  meta?: Record<string, unknown>;
}

export interface LibraryFine {
  id: string;
  amount: number;
  reason?: string;
  dueDate?: string;
}

export interface LibraryHold {
  id: string;
  item_id: string;
  item_title?: string;
  status?: string;
  pickup_location?: string;
  position?: number;
  eta?: string;
}

type ApiResponse<T> = { data?: T };
type ApiListResponse<T> = { data?: T[] };
type ApiPaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

export async function getLibraryBooks(params?: {
  q?: string;
  type?: string;
  language?: string;
}): Promise<LibraryBook[]> {
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.append('q', params.q);
  if (params?.type) queryParams.append('type', params.type);
  if (params?.language) queryParams.append('language', params.language);

  const path = `/library/catalog${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
  const response = await apiFetch<LibraryBook[] | ApiListResponse<LibraryBook> | ApiPaginatedResponse<LibraryBook>>(path);
  
  // Проверяем разные форматы ответа
  if (Array.isArray(response)) {
    return response;
  }
  
  // Пагинированный ответ с results
  if (response && typeof response === 'object' && 'results' in response) {
    return (response as ApiPaginatedResponse<LibraryBook>).results ?? [];
  }
  
  // Ответ с data
  if (response && typeof response === 'object' && 'data' in response) {
    return (response as ApiListResponse<LibraryBook>).data ?? [];
  }
  
  return [];
}

export async function getLibraryFines(): Promise<LibraryFine[]> {
  // Штрафы получаются через /library/loans/my, где есть информация о просрочках
  const response = await apiFetch<LibraryFine[] | ApiListResponse<LibraryFine>>('/library/loans/my');
  
  if (Array.isArray(response)) {
    return response;
  }
  return response?.data ?? [];
}

export async function submitLibraryFinePayment(loanId: string, amount: number, currency: string = 'RUB'): Promise<{ success: boolean }> {
  await apiFetch('/library/fines/payments/intents', {
    method: 'POST',
    body: {
      loan_id: loanId,
      amount,
      currency,
    },
  });
  return { success: true };
}

export async function getLibraryHolds(): Promise<LibraryHold[]> {
  const response = await apiFetch<LibraryHold[] | ApiListResponse<LibraryHold>>('/library/holds/my');
  
  if (Array.isArray(response)) {
    return response;
  }
  return response?.data ?? [];
}

export async function submitLibraryHold(itemId: string, pickupLocation?: string): Promise<{ success: boolean; holdId?: string }> {
  const response = await apiFetch<ApiResponse<{ hold_id: string }>>('/library/holds', {
    method: 'POST',
    body: {
      item_id: itemId,
      pickup_location: pickupLocation || 'Главная библиотека',
    },
  });
  return {
    success: true,
    holdId: response?.data?.hold_id,
  };
}



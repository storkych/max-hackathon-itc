const DEFAULT_BASE_URL = 'https://student-app-api.itc-hub.ru/api/v1';

export class ApiError extends Error {
  public readonly status: number;
  public readonly statusText: string;
  public readonly details?: unknown;

  constructor(status: number, statusText: string, details?: unknown) {
    super(`Request failed with status ${status}: ${statusText}`);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
    this.details = details;
  }
}

export interface ApiRequestOptions extends Omit<RequestInit, 'body' | 'headers'> {
  body?: BodyInit | Record<string, unknown> | null;
  headers?: HeadersInit;
  skipAuth?: boolean;
}

function resolveBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? DEFAULT_BASE_URL;
}

function resolveAccessToken() {
  const envToken = import.meta.env.VITE_API_ACCESS_TOKEN as string | undefined;
  if (envToken?.trim()) {
    return envToken.trim();
  }

  try {
    const stored = window.localStorage.getItem('api_access_token');
    return stored ?? undefined;
  } catch (error) {
    console.warn('Unable to read access token from localStorage', error);
    return undefined;
  }
}

function resolveMaxInitData(): string | undefined {
  // Если внутри мессенджера Max, берем из WebApp.initData
  const { WebApp } = globalThis as typeof globalThis & {
    WebApp?: {
      initData?: string;
    };
  };

  if (WebApp?.initData) {
    return WebApp.initData;
  }

  // Если не внутри мессенджера, используем статичные данные для разработки
  return 'auth_date=1762996354&hash=89cd03a4df8b204e50a80b608c9ef53c80a46c5f11b1e424cfcdd2878fae0368&chat=%7B%22id%22%3A95373502%2C%22type%22%3A%22DIALOG%22%7D&ip=176.107.246.89&user=%7B%22id%22%3A5323614%2C%22first_name%22%3A%22%D0%9C%D0%B0%D0%BA%D1%81%D0%B8%D0%BC%22%2C%22last_name%22%3A%22%22%2C%22username%22%3Anull%2C%22language_code%22%3A%22ru%22%2C%22photo_url%22%3A%22https%3A%2F%2Fi.oneme.ru%2Fi%3Fr%3DBTGBPUwtwgYUeoFhO7rESmr8dFvblSvIWs8aJx_UxnU_HWgqRn-Y9NmRTud43Mjppv0%22%7D&query_id=094a23bd-67b0-486f-a106-3a71095b85cf';
}

async function parseResponseBody(response: Response) {
  const contentType = response.headers.get('content-type');
  if (!contentType) {
    return undefined;
  }

  if (contentType.includes('application/json')) {
    try {
      return await response.json();
    } catch (error) {
      console.warn('Failed to parse JSON response', error);
      return undefined;
    }
  }

  return response.text();
}

export async function apiFetch<TResponse = unknown>(path: string, options: ApiRequestOptions = {}): Promise<TResponse> {
  const baseUrl = resolveBaseUrl().replace(/\/$/, '');
  const requestUrl = path.startsWith('http') ? path : `${baseUrl}${path.startsWith('/') ? '' : '/'}${path}`;
  const { skipAuth, body: requestBody, headers: initialHeaders, ...restOptions } = options;

  const headers = new Headers(initialHeaders);
  headers.set('Accept', 'application/json');

  const init: RequestInit = {
    ...restOptions,
    headers,
  };

  if (requestBody !== undefined) {
    if (requestBody === null) {
      init.body = null;
    } else if (
      requestBody instanceof FormData ||
      requestBody instanceof Blob ||
      requestBody instanceof URLSearchParams ||
      typeof requestBody === 'string'
    ) {
      init.body = requestBody;
    } else if (requestBody instanceof ArrayBuffer || ArrayBuffer.isView(requestBody)) {
      init.body = requestBody as BodyInit;
    } else {
      headers.set('Content-Type', 'application/json');
      init.body = JSON.stringify(requestBody);
    }
  }

  if (!skipAuth) {
    const token = resolveAccessToken();
    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  // Всегда добавляем X-Max-Init-Data для аутентификации в Max мессенджере
  const initData = resolveMaxInitData();
  if (initData && !headers.has('X-Max-Init-Data')) {
    headers.set('X-Max-Init-Data', initData);
  }

  // Логирование запроса
  const method = restOptions.method || 'GET';
  const logHeaders: Record<string, string> = {};
  headers.forEach((value, key) => {
    // Скрываем чувствительные данные
    if (key.toLowerCase() === 'authorization') {
      logHeaders[key] = value.substring(0, 20) + '...';
    } else if (key.toLowerCase() === 'x-max-init-data') {
      logHeaders[key] = value.substring(0, 50) + '...';
    } else {
      logHeaders[key] = value;
    }
  });

  console.log(`[API Request] ${method} ${requestUrl}`, {
    headers: logHeaders,
    body: requestBody ? (typeof requestBody === 'string' ? requestBody : JSON.stringify(requestBody, null, 2)) : undefined,
  });

  const startTime = Date.now();
  const response = await fetch(requestUrl, init);
  const duration = Date.now() - startTime;

  // Логирование ответа
  const responseHeaders: Record<string, string> = {};
  response.headers.forEach((value, key) => {
    responseHeaders[key] = value;
  });

  if (!response.ok) {
    const details = await parseResponseBody(response);
    console.error(`[API Error] ${method} ${requestUrl}`, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
      body: details,
      duration: `${duration}ms`,
    });
    throw new ApiError(response.status, response.statusText, details);
  }

  if (response.status === 204) {
    console.log(`[API Success] ${method} ${requestUrl}`, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
      body: 'No Content',
      duration: `${duration}ms`,
    });
    return undefined as TResponse;
  }

  const data = await parseResponseBody(response);
  console.log(`[API Success] ${method} ${requestUrl}`, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
    body: data,
    duration: `${duration}ms`,
  });
  return data as TResponse;
}

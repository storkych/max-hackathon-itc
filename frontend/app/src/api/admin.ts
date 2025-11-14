import { apiFetch } from './httpClient';

export interface AdminDashboard {
  metrics?: {
    students?: number;
    staff?: number;
    projects?: number;
  };
  academicMetrics?: {
    averageGrade?: number;
    graduationRate?: number;
  };
  news?: Array<{
    id: string;
    title: string;
    source?: string;
    publishedAt?: string;
  }>;
}

type ApiResponse<T> = { data?: T };

export async function getAdminDashboards(): Promise<AdminDashboard> {
  const response = await apiFetch<AdminDashboard | ApiResponse<AdminDashboard>>('/admin/dashboards');
  
  if ('metrics' in (response ?? {}) || 'academicMetrics' in (response ?? {})) {
    return response as AdminDashboard;
  }
  return (response as ApiResponse<AdminDashboard>)?.data ?? {};
}



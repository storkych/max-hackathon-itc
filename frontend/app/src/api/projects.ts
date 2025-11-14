import { apiFetch, ApiError } from './httpClient';

export interface Project {
  id: string;
  title: string;
  summary?: string;
  description?: string;
  description_md?: string;
  code?: string;
  department?: {
    id?: string;
    title?: string;
  };
  owner?: {
    type?: string;
    id?: string;
    display_name?: string;
  };
  owner_type?: string;
  domain_tags?: string[];
  skills_required?: string[];
  skills?: string[];
  education?: {
    ects?: number;
    track?: string;
  };
  format?: string;
  constraints?: {
    format?: string;
    workload_hours_per_week?: number;
  };
  contacts?: {
    email?: string;
    telegram?: string;
  };
  timeline?: {
    start?: string;
    end?: string;
    finish?: string;
  };
  team?: {
    desired_size?: number;
    roles?: Array<
      | string
      | {
          title?: string;
          description?: string;
        }
    >;
  };
  education_format?: string;
  media?: {
    cover_url?: string;
  };
  links?: {
    figma?: string;
    github?: string;
    demo?: string;
  };
  metrics?: {
    applications?: number;
  };
  moderation?: {
    required?: boolean;
  };
  vacancies?: Array<{
    id?: string;
    title?: string;
    role_code?: string;
    experience_level?: string;
    skills?: string[];
    count_open?: number;
    count_total?: number;
    description?: string;
  }>;
  status?: string;
  metadata?: Record<string, unknown>;
  // Для обратной совместимости с моками
  domainTags?: string[];
  stack?: string[];
}

export interface ProjectTask {
  id: string;
  projectId: string;
  title: string;
  status: string;
  assignee?: string;
  dueDate?: string;
}

export interface ProjectTeamMember {
  name: string;
  role: string;
  id?: string;
}

export interface MyProject {
  id: string;
  title: string;
  role?: string;
  stage?: string;
  team?: ProjectTeamMember[];
  timeline?: {
    start?: string;
    end?: string;
  };
}

export interface ProjectApplicationPayload {
  role_code?: string;
  motivation?: string;
  attachments?: Array<{
    name: string;
    url: string;
  }>;
  cv_url?: string;
  portfolio_url?: string;
  consents?: {
    personal_data?: boolean;
  };
}

export interface ProjectApplicationResponse {
  success: boolean;
  applicationId?: string;
}

type ApiListResponse<T> = { data?: T[]; items?: T[] };
type ApiSingleResponse<T> = { data?: T };
type ApiPaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

function unwrapList<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) {
    return payload as T[];
  }
  const obj = payload as ApiListResponse<T>;
  return obj.data ?? obj.items ?? [];
}

function unwrapSingle<T>(payload: unknown): T {
  const obj = payload as ApiSingleResponse<T>;
  return (obj.data ?? payload) as T;
}

export interface GetProjectsParams {
  q?: string;
  domain?: string;
  stack?: string;
  status?: string;
}

export async function getProjectsCatalog(params?: GetProjectsParams): Promise<Project[]> {
  try {
    const queryParams = new URLSearchParams();
    if (params?.q) queryParams.set('q', params.q);
    if (params?.domain) queryParams.set('domain', params.domain);
    if (params?.stack) queryParams.set('stack', params.stack);
    if (params?.status) queryParams.set('status', params.status);

    const path = `/projects${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiFetch<Project[] | ApiListResponse<Project> | ApiPaginatedResponse<Project>>(path);
    
    // Проверяем пагинированный ответ
    let projects: Project[];
    if (response && typeof response === 'object' && 'results' in response) {
      projects = (response as ApiPaginatedResponse<Project>).results ?? [];
    } else {
      projects = unwrapList<Project>(response);
    }

    // Нормализуем данные для обратной совместимости
    return projects.map((p) => ({
      ...p,
      domainTags: p.domain_tags ?? p.domainTags ?? [],
      stack: p.skills_required ?? p.stack ?? [],
    }));
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to fetch projects catalog', error);
  }
}

export async function getMyProjects(): Promise<MyProject[]> {
  try {
    // Получаем проекты, где текущий пользователь является участником
    // Предполагаем, что это можно получить через GET /projects с фильтром или отдельную ручку
    // Пока используем GET /projects и фильтруем на клиенте (или сервер может вернуть только мои проекты)
    const response = await apiFetch<MyProject[] | ApiListResponse<MyProject> | ApiPaginatedResponse<MyProject>>('/projects');
    
    // Проверяем пагинированный ответ
    if (response && typeof response === 'object' && 'results' in response) {
      return (response as ApiPaginatedResponse<MyProject>).results ?? [];
    }
    return unwrapList<MyProject>(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to fetch my projects', error);
  }
}

export async function getProjectById(id: string): Promise<Project> {
  try {
    const response = await apiFetch<Project | ApiSingleResponse<Project>>(`/projects/${id}`);
    const project = unwrapSingle<Project>(response);
    return {
      ...project,
      domainTags: project.domain_tags ?? project.domainTags ?? [],
      stack: project.skills_required ?? project.stack ?? [],
    };
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to fetch project', error);
  }
}

export async function getProjectTasks(projectId?: string): Promise<ProjectTask[]> {
  try {
    // Если projectId не указан, возможно нужно получить задачи по всем проектам пользователя
    // Пока используем GET /projects/:id/tasks для конкретного проекта
    if (projectId) {
      const response = await apiFetch<ProjectTask[] | ApiListResponse<ProjectTask>>(`/projects/${projectId}/tasks`);
      return unwrapList<ProjectTask>(response);
    }
    // Если projectId не указан, возвращаем пустой массив или можно сделать запрос ко всем проектам
    return [];
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to fetch project tasks', error);
  }
}

export async function getProjectTeam(projectId: string): Promise<ProjectTeamMember[]> {
  try {
    const response = await apiFetch<ProjectTeamMember[] | ApiListResponse<ProjectTeamMember>>(`/projects/${projectId}/team`);
    return unwrapList<ProjectTeamMember>(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to fetch project team', error);
  }
}

export async function submitProjectApplication(projectId: string, payload: ProjectApplicationPayload): Promise<ProjectApplicationResponse> {
  try {
    const response = await apiFetch<ProjectApplicationResponse>(`/projects/${projectId}/apply`, {
      method: 'POST',
      body: payload as Record<string, unknown>,
    });
    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to submit project application', error);
  }
}

export async function createProject(payload: Partial<Project>): Promise<Project> {
  try {
    const response = await apiFetch<Project | ApiSingleResponse<Project>>('/projects', {
      method: 'POST',
      body: payload as Record<string, unknown>,
    });
    return unwrapSingle<Project>(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to create project', error);
  }
}

export async function subscribeToProject(projectId: string, channels: string[]): Promise<void> {
  try {
    await apiFetch(`/projects/${projectId}/subscriptions`, {
      method: 'POST',
      body: { channels },
    });
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, 'Failed to subscribe to project', error);
  }
}


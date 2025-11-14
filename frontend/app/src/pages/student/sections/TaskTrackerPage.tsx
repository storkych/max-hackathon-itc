import { useEffect, useMemo, useState } from 'react';
import { Calendar, BellRing, AlertTriangle } from 'lucide-react';
import {
  getMyProjects,
  getProjectTasks,
  subscribeToProject,
  type MyProject,
  type ProjectTask,
} from '../../../api/projects';

const STATUS_CONFIG = [
  { id: 'backlog', label: 'Бэклог', accent: '#ADB5BD' },
  { id: 'in_progress', label: 'В работе', accent: '#0077FF' },
  { id: 'review', label: 'На ревью', accent: '#F2994A' },
  { id: 'blocked', label: 'Заблокировано', accent: '#E74C3C' },
  { id: 'done', label: 'Завершено', accent: '#27AE60' },
];

const STATUS_ALIASES: Record<string, string> = {
  todo: 'backlog',
  planned: 'backlog',
  backlog: 'backlog',
  in_progress: 'in_progress',
  working: 'in_progress',
  doing: 'in_progress',
  review: 'review',
  qa: 'review',
  blocked: 'blocked',
  risk: 'blocked',
  done: 'done',
  completed: 'done',
  success: 'done',
};

function mapStatus(status?: string) {
  if (!status) return 'backlog';
  const normalized = status.toLowerCase();
  return STATUS_ALIASES[normalized] ?? (STATUS_CONFIG.some((cfg) => cfg.id === normalized) ? normalized : 'backlog');
}

export function TaskTrackerPage() {
  const [tasks, setTasks] = useState<ProjectTask[]>([]);
  const [projects, setProjects] = useState<MyProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeProjectId, setActiveProjectId] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [subscribing, setSubscribing] = useState<string | null>(null);
  const [subscribeMessage, setSubscribeMessage] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const myProjects = await getMyProjects();
        setProjects(Array.isArray(myProjects) ? myProjects : []);

        const allTasks: ProjectTask[] = [];
        await Promise.all(
          (myProjects ?? []).map(async (project) => {
            try {
              const projectTasks = await getProjectTasks(project.id);
              allTasks.push(...projectTasks);
            } catch (error) {
              console.error(`Failed to load tasks for project ${project.id}`, error);
            }
          }),
        );
        setTasks(allTasks);
      } catch (error) {
        console.error('Failed to load task tracker data', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filteredTasks = useMemo(() => {
    const term = search.trim().toLowerCase();
    return tasks.filter((task) => {
      const matchProject = activeProjectId === 'all' || task.projectId === activeProjectId;
      if (!term) {
        return matchProject;
      }
      const fields = [task.title, task.status, task.assignee].filter(Boolean).map((value) => value!.toLowerCase());
      return matchProject && fields.some((value) => value.includes(term));
    });
  }, [tasks, activeProjectId, search]);

  const tasksByStatus = useMemo(() => {
    return STATUS_CONFIG.map((config) => ({
      ...config,
      tasks: filteredTasks.filter((task) => mapStatus(task.status) === config.id),
    }));
  }, [filteredTasks]);

  const overdueTasks = useMemo(() => {
    const now = new Date();
    return filteredTasks.filter(
      (task) => task.dueDate && new Date(task.dueDate).getTime() < now.getTime() && mapStatus(task.status) !== 'done',
    );
  }, [filteredTasks]);

  const handleSubscribe = async () => {
    if (activeProjectId === 'all') {
      setSubscribeMessage('Сначала выберите конкретный проект.');
      return;
    }
    setSubscribeMessage(null);
    setSubscribing(activeProjectId);
    try {
      await subscribeToProject(activeProjectId, ['in_app', 'email']);
      setSubscribeMessage('Подписка на уведомления оформлена.');
    } catch (error) {
      console.error('Failed to subscribe to project', error);
      setSubscribeMessage('Не удалось оформить подписку. Попробуйте позже.');
    } finally {
      setSubscribing(null);
    }
  };

  const currentProject = projects.find((project) => project.id === activeProjectId);

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Таск-трекер</h1>
            <p className="subtitle">Задачи по вашим проектам MAX Campus</p>
          </div>
        </div>

        <div className="task-toolbar">
          <select
            className="form-input"
            value={activeProjectId}
            onChange={(event) => setActiveProjectId(event.target.value)}
            disabled={projects.length === 0}
          >
            <option value="all">Все проекты</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.title}
              </option>
            ))}
          </select>
          <input
            className="form-input"
            type="search"
            placeholder="Поиск по названию, статусу или исполнителю"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            disabled={loading}
          />
          <button
            className="btn btn-secondary task-subscribe-btn"
            type="button"
            onClick={handleSubscribe}
            disabled={subscribing !== null}
          >
            <BellRing size={18} />
            {subscribing !== null ? 'Оформляем...' : 'Получать уведомления'}
          </button>
        </div>
        {subscribeMessage && <div className="card-description">{subscribeMessage}</div>}

        <div className="task-summary">
          <div className="task-summary-card">
            <div className="task-summary-label">Задач на проект</div>
            <div className="task-summary-value">{filteredTasks.length}</div>
          </div>
          <div className="task-summary-card">
            <div className="task-summary-label">Просрочено</div>
            <div className="task-summary-value task-summary-value--danger">{overdueTasks.length}</div>
          </div>
          {currentProject && currentProject.team && (
            <div className="task-summary-card">
              <div className="task-summary-label">Команда проекта</div>
              <div className="task-summary-value">{currentProject.team.length} чел.</div>
            </div>
          )}
        </div>

        <div className="task-board">
          {STATUS_CONFIG.map((config) => {
            const columnTasks = tasksByStatus.find((group) => group.id === config.id)?.tasks ?? [];
            return (
              <div key={config.id} className="task-column">
                <div className="task-column-header">
                  <span>
                    {config.label} <sup>{columnTasks.length}</sup>
                  </span>
                </div>
                <div className="task-column-body">
                  {loading ? (
                    Array.from({ length: 2 }).map((_, index) => (
                      <div key={`${config.id}-skeleton-${index}`} className="task-card task-card--skeleton">
                        <div className="skeleton-line" style={{ width: '80%' }} />
                        <div className="skeleton-line" style={{ width: '60%' }} />
                        <div className="skeleton-line" style={{ width: '50%' }} />
                      </div>
                    ))
                  ) : columnTasks.length === 0 ? (
                    <div className="task-column-empty">Нет задач</div>
                  ) : (
                    columnTasks.map((task) => {
                      const project = projects.find((p) => p.id === task.projectId);
                      return (
                        <div key={task.id} className="task-card">
                          <div className="task-card-title">{task.title}</div>
                          <div className="task-card-meta">
                            <span>{project?.title ?? 'Проект'}</span>
                            {task.dueDate && (
                              <span>
                                <Calendar size={14} />
                                {new Date(task.dueDate).toLocaleDateString('ru-RU')}
                              </span>
                            )}
                          </div>
                          <div className="task-card-footer">
                            <span className="task-pastille" style={{ background: config.accent }}>
                              {config.label}
                            </span>
                            <span className="task-assignee">{task.assignee ?? 'Без исполнителя'}</span>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {overdueTasks.length > 0 && (
          <div className="card task-alert-card">
            <div className="task-alert-icon">
              <AlertTriangle size={20} />
            </div>
            <div>
              <div className="task-alert-title">Есть просроченные задачи</div>
              <div className="task-alert-description">
                {overdueTasks.map((task) => {
                  const project = projects.find((p) => p.id === task.projectId);
                  return (
                    <div key={task.id}>
                      <strong>{task.title}</strong> • {project?.title ?? task.projectId}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


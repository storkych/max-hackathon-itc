import { useEffect, useMemo, useState } from 'react';
import { Calendar, Briefcase, Users, Mail, Layers, Tag, ExternalLink, ChevronRight } from 'lucide-react';
import {
  getMyProjects,
  getProjectsCatalog,
  submitProjectApplication,
  type MyProject,
  type Project,
} from '../../../api/projects';

const FALLBACK_COVER =
  'data:image/svg+xml;charset=UTF-8,' +
  encodeURIComponent(
    `<svg width="320" height="160" xmlns="http://www.w3.org/2000/svg">
      <rect width="320" height="160" rx="16" fill="#E9ECEF"/>
      <text x="50%" y="50%" text-anchor="middle" fill="#ADB5BD" font-family="Arial" font-size="16">MAX</text>
    </svg>`,
  );

type ProjectsTab = 'my' | 'catalog';

interface ProjectsPageProps {
  initialTab?: ProjectsTab;
}

export function ProjectsPage({ initialTab = 'my' }: ProjectsPageProps) {
  const [myProjects, setMyProjects] = useState<MyProject[]>([]);
  const [catalog, setCatalog] = useState<Project[]>([]);
  const [loadingMy, setLoadingMy] = useState(true);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [applicationStatus, setApplicationStatus] = useState<Record<string, 'idle' | 'submitting' | 'success'>>({});
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<ProjectsTab>(initialTab);

  useEffect(() => {
    setActiveTab(initialTab);
  }, [initialTab]);

  useEffect(() => {
    const loadMine = async () => {
      try {
        const data = await getMyProjects();
        setMyProjects(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Failed to load my projects', error);
      } finally {
        setLoadingMy(false);
      }
    };
    loadMine();
  }, []);

  useEffect(() => {
    const loadCatalog = async () => {
      try {
        const data = await getProjectsCatalog();
        setCatalog(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Failed to load projects catalog', error);
      } finally {
        setLoadingCatalog(false);
      }
    };
    loadCatalog();
  }, []);

  const filteredCatalog = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) {
      return catalog;
    }
    return catalog.filter((project) => {
      const fields = [
        project.title,
        project.summary,
        project.department?.title,
        ...(project.domain_tags ?? []),
        ...(project.skills_required ?? []),
        project.description,
      ]
        .filter(Boolean)
        .map((value) => value!.toLowerCase());
      return fields.some((value) => value.includes(term));
    });
  }, [catalog, search]);

  const buildApplicationPayload = (project: Project) => {
    const primaryVacancy = project.vacancies?.[0];
    const roleCode = primaryVacancy?.role_code ?? project.skills_required?.[0] ?? 'team-member';
    return {
      role_code: roleCode,
      motivation: `Готов взять на себя роль ${roleCode} в проекте ${project.title}.`,
      attachments: [
        {
          name: 'cv.pdf',
          url: 'https://example.com/cv.pdf',
        },
      ],
      cv_url: 'https://example.com/cv.pdf',
      portfolio_url: 'https://github.com/example',
      consents: {
        personal_data: true,
      },
    };
  };

  const handleProjectApply = async (project: Project) => {
    setApplicationStatus((prev) => ({ ...prev, [project.id]: 'submitting' }));
    try {
      const payload = buildApplicationPayload(project);
      await submitProjectApplication(project.id, payload);
      setApplicationStatus((prev) => ({ ...prev, [project.id]: 'success' }));
    } catch (error) {
      console.error('Failed to submit project application', error);
      setApplicationStatus((prev) => ({ ...prev, [project.id]: 'idle' }));
    }
  };

  const formatTimeline = (project: MyProject) => {
    if (!project.timeline) {
      return null;
    }
    const { start, end } = project.timeline;
    if (start && end) {
      return `${start} — ${end}`;
    }
    return start ?? end ?? null;
  };

  const formatCatalogTimeline = (project: Project) => {
    if (!project.timeline) return null;
    const start = project.timeline.start;
    const end = project.timeline.end ?? (project.timeline as { finish?: string }).finish;
    if (start && end) {
      return `${start} — ${end}`;
    }
    return start ?? end ?? null;
  };

  const formatVacancies = (project: Project) => {
    if (!project.vacancies || project.vacancies.length === 0) {
      return null;
    }
    const total = project.vacancies.reduce((sum, vacancy) => sum + (vacancy.count_total ?? 0), 0);
    const open = project.vacancies.reduce((sum, vacancy) => sum + (vacancy.count_open ?? 0), 0);
    return `${open} из ${total} ролей свободны`;
  };

  const renderMyProjects = () => {
    if (loadingMy) {
      return (
        <div className="projects-grid">
          {Array.from({ length: 2 }).map((_, index) => (
            <div key={`my-project-skeleton-${index}`} className="card project-card project-card--skeleton">
              <div className="project-cover skeleton-block" />
              <div className="project-card-body">
                <div className="skeleton-line" style={{ width: '60%' }} />
                <div className="skeleton-line" style={{ width: '40%' }} />
                <div className="skeleton-line" style={{ width: '80%' }} />
                <div className="skeleton-chip-row">
                  <span className="skeleton-chip" />
                  <span className="skeleton-chip" />
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (myProjects.length === 0) {
      return <div className="card-description">У вас пока нет активных проектов.</div>;
    }

    return (
      <div className="projects-grid">
        {myProjects.map((project) => {
          const timeline = formatTimeline(project);
          return (
            <div key={project.id} className="card project-card project-card--compact">
              <div className="project-card-body">
                <div className="project-card-header">
                  <div>
                    <div className="project-category">Участие</div>
                    <h2>{project.title}</h2>
                    {project.role && <p className="project-summary">{project.role}</p>}
                  </div>
                  {project.stage && <span className="project-status">{project.stage}</span>}
                </div>

                <div className="project-meta">
                  {timeline && (
                    <span>
                      <Calendar size={16} />
                      {timeline}
                    </span>
                  )}
                  {project.team && project.team.length > 0 && (
                    <span>
                      <Users size={16} />
                      Команда: {project.team.length} чел.
                    </span>
                  )}
                </div>

                {project.team && project.team.length > 0 && (
                  <div className="project-section">
                    <div className="project-section-label">Команда</div>
                    <div className="project-team-list">
                      {project.team.map((member) => (
                        <div key={member.id ?? member.name} className="project-team-row">
                          <span>{member.name}</span>
                          <span className="project-team-role">{member.role}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="project-actions">
                  <button className="btn btn-secondary project-apply-btn" type="button">
                    Смотреть детали <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderCatalog = () => {
    if (loadingCatalog) {
      return (
        <div className="projects-grid">
          {Array.from({ length: 2 }).map((_, index) => (
            <div key={`catalog-skeleton-${index}`} className="card project-card project-card--skeleton">
              <div className="project-cover skeleton-block" />
              <div className="project-card-body">
                <div className="skeleton-line" style={{ width: '45%' }} />
                <div className="skeleton-line" style={{ width: '70%' }} />
                <div className="skeleton-line" style={{ width: '90%' }} />
                <div className="skeleton-chip-row">
                  <span className="skeleton-chip" />
                  <span className="skeleton-chip" />
                </div>
                <div className="skeleton-button" />
              </div>
            </div>
          ))}
        </div>
      );
    }

    if (filteredCatalog.length === 0) {
      return <div className="card-description">Нет проектов по заданным критериям.</div>;
    }

    return (
      <div className="projects-grid">
        {filteredCatalog.map((project) => {
          const status = applicationStatus[project.id] ?? 'idle';
          const timeline = formatCatalogTimeline(project);
          const vacanciesLabel = formatVacancies(project);
          const coverSrc =
            project.media?.cover_url && !project.media.cover_url.includes('example.com')
              ? project.media.cover_url
              : FALLBACK_COVER;

          return (
            <div key={project.id} className="card project-card">
              <div className="project-cover" style={{ backgroundImage: `url(${coverSrc})` }} aria-hidden="true" />
              <div className="project-card-body">
                <div className="project-card-header">
                  <div>
                    <div className="project-category">{project.department?.title ?? 'Проект кампуса'}</div>
                    <h2>{project.title}</h2>
                    {project.summary && <p className="project-summary">{project.summary}</p>}
                  </div>
                  {project.status && <span className={`project-status project-status--${project.status}`}>{project.status}</span>}
                </div>

                <div className="project-meta">
                  {timeline && (
                    <span>
                      <Calendar size={16} />
                      {timeline}
                    </span>
                  )}
                  {project.format && (
                    <span>
                      <Layers size={16} />
                      {project.format}
                    </span>
                  )}
                  {project.owner?.display_name && (
                    <span>
                      <Users size={16} />
                      Куратор: {project.owner.display_name}
                    </span>
                  )}
                  {project.contacts?.email && (
                    <span>
                      <Mail size={16} />
                      {project.contacts.email}
                    </span>
                  )}
                </div>

                <div className="project-chip-row">
                  {project.domain_tags?.map((tag) => (
                    <span key={`${project.id}-domain-${tag}`} className="project-chip">
                      <Tag size={14} />
                      {tag}
                    </span>
                  ))}
                  {project.skills_required?.map((skill) => (
                    <span key={`${project.id}-skill-${skill}`} className="project-chip project-chip--ghost">
                      {skill}
                    </span>
                  ))}
                </div>

                {project.description && <p className="project-description">{project.description}</p>}

                <div className="project-sections">
                  {project.education && (
                    <div className="project-section">
                      <div className="project-section-label">Обучение</div>
                      <div className="project-section-content">
                        {project.education.track && <span>Трек: {project.education.track}</span>}
                        {project.education.ects && <span>ECTS: {project.education.ects}</span>}
                      </div>
                    </div>
                  )}

                  {project.team?.roles && project.team.roles.length > 0 && (
                    <div className="project-section">
                      <div className="project-section-label">Команда</div>
                      {project.team.desired_size && (
                        <div className="project-meta project-meta--inline">
                          <span>
                            <Users size={16} />
                            Планируется {project.team.desired_size} человек
                          </span>
                        </div>
                      )}
                      <div className="project-role-grid">
                        {project.team.roles.map((role, index) => {
                          if (typeof role === 'string') {
                            return (
                              <div key={`${project.id}-role-${index}`} className="project-role-card">
                                <strong>{role}</strong>
                              </div>
                            );
                          }
                          return (
                            <div key={`${project.id}-role-${index}`} className="project-role-card">
                              <strong>{role.title ?? 'Роль'}</strong>
                              {role.description && <p>{role.description}</p>}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {project.vacancies && project.vacancies.length > 0 && (
                    <div className="project-section">
                      <div className="project-section-label">Открытые роли</div>
                      <div className="project-vacancy">
                        <Briefcase size={16} />
                        <span>{vacanciesLabel}</span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="project-actions">
                  {project.links?.figma && (
                    <a href={project.links.figma} target="_blank" rel="noreferrer" className="project-link">
                      <ExternalLink size={16} />
                      Макет
                    </a>
                  )}
                  <button
                    className="btn project-apply-btn"
                    type="button"
                    onClick={() => handleProjectApply(project)}
                    disabled={status === 'submitting'}
                  >
                    {status === 'success'
                      ? 'Заявка отправлена'
                      : status === 'submitting'
                        ? 'Отправляем...'
                        : 'Откликнуться'}
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Проекты</h1>
            <p className="subtitle">Отслеживайте свои проекты и находите новые инициативы</p>
          </div>
        </div>

        <div className="library-tabs project-tabs">
          <button
            type="button"
            className={`library-tab${activeTab === 'my' ? ' library-tab--active' : ''}`}
            onClick={() => setActiveTab('my')}
          >
            Мои проекты
          </button>
          <button
            type="button"
            className={`library-tab${activeTab === 'catalog' ? ' library-tab--active' : ''}`}
            onClick={() => setActiveTab('catalog')}
          >
            Каталог
          </button>
        </div>

        {activeTab === 'catalog' && (
          <div className="projects-toolbar">
            <input
              className="form-input"
              type="search"
              placeholder="Поиск по проектам и ролям"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              disabled={loadingCatalog}
            />
          </div>
        )}

        {activeTab === 'my' ? renderMyProjects() : renderCatalog()}
      </div>
    </div>
  );
}


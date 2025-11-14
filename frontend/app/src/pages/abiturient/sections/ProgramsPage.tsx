import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, Clock, Target, TrendingUp } from 'lucide-react';
import { useAppState } from '../../../context/AppStateContext';
import {
  getAdmissionsPrograms,
  type AdmissionsProgram,
  type AdmissionsProgramFilters,
} from '../../../api/admissions';

const LEVEL_LABELS: Record<string, string> = {
  bachelor: 'Бакалавриат',
  master: 'Магистратура',
  specialist: 'Специалитет',
  postgraduate: 'Аспирантура',
};

const FORMAT_LABELS: Record<string, string> = {
  full_time: 'Очная',
  part_time: 'Заочная',
  distance: 'Дистанционная',
  evening: 'Вечерняя',
};

const FALLBACK_PROGRAM_COVER =
  'data:image/svg+xml;charset=UTF-8,' +
  encodeURIComponent(
    `<svg width="640" height="360" xmlns="http://www.w3.org/2000/svg">
      <rect width="640" height="360" fill="#E9ECEF" rx="24"/>
      <text x="50%" y="50%" text-anchor="middle" fill="#ADB5BD" font-family="Inter, Arial" font-size="48" letter-spacing="0.3em">MAX</text>
    </svg>`,
  );

function formatLevel(level?: string) {
  if (!level) return 'Уровень уточняется';
  return LEVEL_LABELS[level] ?? level;
}

function formatFormat(format?: string) {
  if (!format) return 'Формат уточняется';
  return FORMAT_LABELS[format] ?? format;
}

function formatCurrency(value?: string) {
  if (!value) return 'Стоимость уточняется';
  if (Number.isFinite(Number(value))) {
    return `${Number(value).toLocaleString('ru-RU')} ₽/год`;
  }
  return value.endsWith('₽') ? value : `${value} ₽`;
}

function getDeadlineLabel(date?: string) {
  if (!date) return 'Приём документов открыт';
  const formatter = new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long' });
  return `Дедлайн: ${formatter.format(new Date(date))}`;
}

function getCoverSrc(program: AdmissionsProgram) {
  const cover = program.media?.coverUrl;
  if (!cover || cover.includes('example.com')) {
    return FALLBACK_PROGRAM_COVER;
  }
  return cover;
}

export function ProgramsPage() {
  const { selectedUniversityId } = useAppState();
  const navigate = useNavigate();
  const [programs, setPrograms] = useState<AdmissionsProgram[]>([]);
  const [filters, setFilters] = useState<AdmissionsProgramFilters | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [level, setLevel] = useState('all');
  const [format, setFormat] = useState('all');
  const [department, setDepartment] = useState('all');

  const levelOptions = useMemo(() => filters?.levels ?? [], [filters]);
  const formatOptions = useMemo(() => filters?.formats ?? [], [filters]);
  const departmentOptions = useMemo(() => filters?.departments ?? [], [filters]);

  useEffect(() => {
    if (!selectedUniversityId) {
      navigate('/');
      return;
    }

    let mounted = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const { programs: programsResponse, filters: filtersResponse } = await getAdmissionsPrograms(selectedUniversityId);
        if (mounted) {
          setPrograms(programsResponse);
          setFilters(filtersResponse);
        }
      } catch (loadError) {
        console.error('Failed to load programs', loadError);
        if (mounted) {
          setError('Не удалось загрузить программы обучения.');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      mounted = false;
    };
  }, [selectedUniversityId, navigate]);

  const filteredPrograms = useMemo(() => {
    const term = search.trim().toLowerCase();
    return programs.filter((program) => {
      const matchesLevel = level === 'all' || program.level === level;
      const matchesFormat = format === 'all' || program.format === format;
      const matchesDepartment = department === 'all' || program.department?.id === department;

      if (!term) {
        return matchesLevel && matchesFormat && matchesDepartment;
      }
      const haystack = [
        program.title,
        program.description,
        program.department?.title,
        program.careerPaths?.join(' '),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return matchesLevel && matchesFormat && matchesDepartment && haystack.includes(term);
    });
  }, [programs, level, format, department, search]);

  const stats = useMemo(() => {
    if (!programs.length) {
      return { budget: 0, paid: 0, averageScore: 0, closestDeadline: null as string | null };
    }
    const budget = programs.reduce((sum, program) => sum + (program.budgetSeats ?? 0), 0);
    const paid = programs.reduce((sum, program) => sum + (program.paidSeats ?? 0), 0);
    const scores = programs.map((program) => program.passingScore).filter((value): value is number => typeof value === 'number');
    const averageScore = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    const futureDeadlines = programs
      .map((program) => program.admissionDeadline)
      .filter((date): date is string => Boolean(date))
      .sort((a, b) => new Date(a).getTime() - new Date(b).getTime());
    return {
      budget,
      paid,
      averageScore,
      closestDeadline: futureDeadlines[0] ?? null,
    };
  }, [programs]);

  const resetFilters = () => {
    setLevel('all');
    setFormat('all');
    setDepartment('all');
    setSearch('');
  };

  const renderSkeleton = () => (
    <div className="programs-grid">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={`program-skeleton-${index}`} className="program-card program-card--skeleton">
          <div className="program-card-cover" />
          <div className="program-card-body">
            <div className="skeleton-line" style={{ width: '60%' }} />
            <div className="skeleton-line" style={{ width: '80%' }} />
            <div className="skeleton-line" style={{ width: '90%' }} />
            <div className="skeleton-line" style={{ width: '70%' }} />
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Образовательные программы</h1>
            <p className="subtitle">Найдите подходящий трек обучения и узнайте про бюджетные места, дедлайны и карьерные возможности.</p>
          </div>
        </div>

        {loading ? (
          renderSkeleton()
        ) : error ? (
          <div className="card">
            <div className="card-title">Ошибка</div>
            <div className="card-description">{error}</div>
          </div>
        ) : (
          <>
            <div className="programs-stats">
              <div className="programs-stat-card">
                <Bookmark size={18} />
                <div>
                  <div className="programs-stat-label">Программ найдено</div>
                  <div className="programs-stat-value">
                    {filteredPrograms.length} / {programs.length}
                  </div>
                </div>
              </div>
              <div className="programs-stat-card">
                <Target size={18} />
                <div>
                  <div className="programs-stat-label">Бюджетных мест</div>
                  <div className="programs-stat-value">{stats.budget.toLocaleString('ru-RU')}</div>
                </div>
              </div>
              <div className="programs-stat-card">
                <TrendingUp size={18} />
                <div>
                  <div className="programs-stat-label">Средний проходной</div>
                  <div className="programs-stat-value">{stats.averageScore || '—'}</div>
                </div>
              </div>
              <div className="programs-stat-card">
                <Clock size={18} />
                <div>
                  <div className="programs-stat-label">Ближайший дедлайн</div>
                  <div className="programs-stat-value">
                    {stats.closestDeadline
                      ? new Date(stats.closestDeadline).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
                      : 'Актуально круглый год'}
                  </div>
                </div>
              </div>
            </div>

            <div className="programs-toolbar">
              <input
                type="search"
                className="form-input"
                placeholder="Поиск по названию, кафедре или карьере"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
              <select className="form-input" value={level} onChange={(event) => setLevel(event.target.value)}>
                <option value="all">Все уровни</option>
                {levelOptions.map((item, index) => (
                  <option key={`${item}-${index}`} value={item}>
                    {formatLevel(item)}
                  </option>
                ))}
              </select>
              <select className="form-input" value={format} onChange={(event) => setFormat(event.target.value)}>
                <option value="all">Все форматы</option>
                {formatOptions.map((item, index) => (
                  <option key={`${item}-${index}`} value={item}>
                    {formatFormat(item)}
                  </option>
                ))}
              </select>
              <select className="form-input" value={department} onChange={(event) => setDepartment(event.target.value)}>
                <option value="all">Все кафедры</option>
                {departmentOptions.map((item) => (
                  <option key={`${item.id}-${item.title}`} value={item.id}>
                    {item.title}
                  </option>
                ))}
              </select>
              <button type="button" className="btn btn-secondary" onClick={resetFilters}>
                Сбросить
              </button>
            </div>

            {filteredPrograms.length === 0 ? (
              <div className="card">
                <div className="card-title">Ничего не найдено</div>
                <div className="card-description">Попробуйте изменить фильтры или поиск.</div>
              </div>
            ) : (
              <div className="programs-grid">
                {filteredPrograms.map((program) => {
                  const totalSeats = (program.budgetSeats ?? 0) + (program.paidSeats ?? 0);
                  const budgetPercent = totalSeats ? Math.round(((program.budgetSeats ?? 0) / totalSeats) * 100) : 0;
                  const coverSrc = getCoverSrc(program);
                  return (
                    <div key={program.id} className="program-card">
                      <div className="program-card-cover" aria-hidden="true" style={{ backgroundImage: `url(${coverSrc})` }} />
                      <div className="program-card-body">
                        <div className="program-card-tags">
                          <span className="program-chip">{formatLevel(program.level)}</span>
                          <span className="program-chip program-chip--ghost">{formatFormat(program.format)}</span>
                          {program.language && <span className="program-chip program-chip--muted">{program.language.toUpperCase()}</span>}
                        </div>
                        <h2>{program.title}</h2>
                        {program.description && <p className="program-description">{program.description}</p>}

                        <div className="program-meta">
                          <span>Кафедра: {program.department?.title ?? 'уточняется'}</span>
                          <span>Продолжительность: {program.duration ?? `${program.durationYears ?? '?'} года`}</span>
                          <span>Стоимость: {formatCurrency(program.tuitionPerYear ?? program.tuition)}</span>
                          <span>{getDeadlineLabel(program.admissionDeadline)}</span>
                        </div>

                        <div className="program-capacity">
                          <div className="program-capacity-bar">
                            <span style={{ width: `${budgetPercent}%` }} />
                          </div>
                          <div className="program-capacity-labels">
                            <span>Бюджет: {program.budgetSeats ?? '—'}</span>
                            <span>Платно: {program.paidSeats ?? '—'}</span>
                            {program.targetedSeats ? <span>Целевых: {program.targetedSeats}</span> : null}
                          </div>
                        </div>

                        {program.exams?.length ? (
                          <div className="program-badges">
                            {program.exams.map((exam, examIndex) => (
                              <span key={`${program.id}-exam-${examIndex}`} className="program-badge">
                                {exam}
                              </span>
                            ))}
                          </div>
                        ) : null}

                        {program.careerPaths?.length ? (
                          <div className="program-career-chips">
                            {program.careerPaths.map((career, careerIndex) => (
                              <span key={`${program.id}-career-${careerIndex}`} className="program-chip program-chip--ghost">
                                {career}
                              </span>
                            ))}
                          </div>
                        ) : null}

                        <div className="program-card-footer">
                          {program.passingScore ? (
                            <div>
                              <span className="program-card-footer-label">Проходной балл 2024</span>
                              <div className="program-card-footer-value">{program.passingScore}</div>
                            </div>
                          ) : null}
                          {program.links?.landing ? (
                            <a href={program.links.landing} className="btn program-link-btn" target="_blank" rel="noreferrer">
                              Подробнее
                            </a>
                          ) : (
                            <button className="btn program-link-btn" type="button" disabled>
                              Подробности скоро
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}


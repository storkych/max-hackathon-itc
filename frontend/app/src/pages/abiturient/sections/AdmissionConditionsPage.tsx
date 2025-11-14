import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../../../context/AppStateContext';
import {
  getAdmissionsPrograms,
  getProgramRequirements,
  type AdmissionsProgram,
  type ProgramRequirement,
} from '../../../api/admissions';

interface ProgramRequirementEntry {
  program: AdmissionsProgram;
  requirement: ProgramRequirement;
}

const LEVEL_LABELS: Record<string, string> = {
  bachelor: 'Бакалавриат',
  master: 'Магистратура',
  masster: 'Магистратура',
  specialist: 'Специалитет',
  postgraduate: 'Аспирантура',
};

const FORMAT_LABELS: Record<string, string> = {
  full_time: 'Очная',
  'full time': 'Очная',
  part_time: 'Заочная',
  'part time': 'Заочная',
  distance: 'Дистанционная',
  evening: 'Вечерняя',
};

function normalizeKey(value?: string) {
  if (!value) return '';
  return value
    .toLowerCase()
    .replace(/[^a-zа-я0-9]+/gi, '_')
    .replace(/^_+|_+$/g, '');
}

function formatLevel(level?: string) {
  const key = normalizeKey(level);
  return LEVEL_LABELS[key] ?? (level ? level.charAt(0).toUpperCase() + level.slice(1).toLowerCase() : 'Уровень уточняется');
}

function formatFormat(format?: string) {
  const key = normalizeKey(format);
  return FORMAT_LABELS[key] ?? (format ? format.charAt(0).toUpperCase() + format.slice(1).toLowerCase() : 'Формат уточняется');
}

export function AdmissionConditionsPage() {
  const { selectedUniversityId } = useAppState();
  const navigate = useNavigate();
  const [programs, setPrograms] = useState<AdmissionsProgram[]>([]);
  const [requirements, setRequirements] = useState<ProgramRequirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeProgramId, setActiveProgramId] = useState<string>('');

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
        const { programs: programsResponse } = await getAdmissionsPrograms(selectedUniversityId);
        const requirementsResponse = await Promise.all(
          programsResponse.map(async (program) => {
            const requirement = await getProgramRequirements(program.id);
            return requirement;
          }),
        );

        if (!mounted) {
          return;
        }

        setPrograms(programsResponse);
        setRequirements(requirementsResponse.filter(Boolean) as ProgramRequirement[]);
      } catch (loadError) {
        console.error('Failed to load admission requirements', loadError);
        if (mounted) {
          setError('Не удалось загрузить требования к поступлению.');
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

  const requirementEntries = useMemo<ProgramRequirementEntry[]>(() => {
    const map = new Map<string, ProgramRequirement>();
    requirements.forEach((requirement) => {
      map.set(requirement.programId, requirement);
    });
    return programs
      .map((program) => {
        const requirement = map.get(program.id);
        if (!requirement) {
          return null;
        }
        return { program, requirement };
      })
      .filter((entry): entry is ProgramRequirementEntry => Boolean(entry));
  }, [programs, requirements]);

  useEffect(() => {
    if (!activeProgramId && requirementEntries.length > 0) {
      setActiveProgramId(requirementEntries[0].program.id);
    }
  }, [activeProgramId, requirementEntries]);

  const activeEntry = requirementEntries.find((entry) => entry.program.id === activeProgramId) ?? requirementEntries[0] ?? null;

  const stats = useMemo(() => {
    if (!requirementEntries.length) {
      return { count: 0, averageScore: 0, totalSubjects: 0 };
    }
    const totalScore = requirementEntries.reduce((sum, entry) => sum + (entry.requirement.minScore ?? 0), 0);
    const totalSubjects = requirementEntries.reduce((sum, entry) => sum + entry.requirement.subjects.length, 0);
    return {
      count: requirementEntries.length,
      averageScore: Math.round(totalScore / requirementEntries.length) || '—',
      totalSubjects,
    };
  }, [requirementEntries]);

  const renderSkeleton = () => (
    <div className="admission-grid">
      {Array.from({ length: 2 }).map((_, index) => (
        <div key={`admission-skeleton-${index}`} className="card admission-card admission-card--skeleton">
          <div className="skeleton-line" style={{ width: '60%' }} />
          <div className="skeleton-line" style={{ width: '40%' }} />
          <div className="skeleton-line" style={{ width: '80%' }} />
          <div className="skeleton-line" style={{ width: '50%' }} />
        </div>
      ))}
    </div>
  );

  const renderContent = () => {
    if (loading) {
      return renderSkeleton();
    }

    if (error) {
      return (
        <div className="card">
          <div className="card-title">Ошибка</div>
          <div className="card-description">{error}</div>
        </div>
      );
    }

    if (!requirementEntries.length) {
      return (
        <div className="card">
          <div className="card-title">Требования не найдены</div>
          <div className="card-description">Для выбранного вуза пока нет опубликованных условий поступления.</div>
        </div>
      );
    }

    if (!activeEntry) {
      return null;
    }

    const { program, requirement } = activeEntry;
    const yearLabel = requirement.year ?? 'Год уточняется';

    return (
      <>
        <div className="admission-hero card">
          <div>
            <h1>Условия поступления</h1>
            <p className="subtitle">Ознакомьтесь с минимальными баллами, перечнем экзаменов и документами для вступительной кампании.</p>
          </div>
          <div className="admission-hero-stats">
            <div>
              <div className="admission-stat-label">Программ с требованиями</div>
              <div className="admission-stat-value">{stats.count}</div>
            </div>
            <div>
              <div className="admission-stat-label">Средний проходной</div>
              <div className="admission-stat-value">{stats.averageScore}</div>
            </div>
            <div>
              <div className="admission-stat-label">Суммарно предметов</div>
              <div className="admission-stat-value">{stats.totalSubjects}</div>
            </div>
          </div>
        </div>

        <div className="admission-toolbar">
          <select className="form-input" value={activeProgramId} onChange={(event) => setActiveProgramId(event.target.value)}>
            {requirementEntries.map((entry) => (
              <option key={entry.program.id} value={entry.program.id}>
                {entry.program.title}
              </option>
            ))}
          </select>
          <div className="admission-toolbar-info">
            <span>{formatLevel(program.level)}</span>
            <span>{formatFormat(program.format)}</span>
            <span>Продолжительность: {program.duration ?? `${program.durationYears ?? '?'} года`}</span>
          </div>
        </div>

        <div className="admission-grid">
          <div className="card admission-card">
            <div className="admission-card-header">
              <span className="admission-year">{yearLabel}</span>
              <span className="admission-min-score">
                {requirement.minScore ?? '—'}
                <small>минимальный балл</small>
              </span>
            </div>
            <p className="admission-card-description">
              Для поступления на программу <strong>{program.title}</strong> необходимо набрать суммарно не менее указанного проходного балла.
            </p>
            <div className="admission-metrics">
              <div>
                <div className="admission-metric-label">Предметов</div>
                <div className="admission-metric-value">{requirement.subjects.length}</div>
              </div>
              <div>
                <div className="admission-metric-label">Спец. условия</div>
                <div className="admission-metric-value">{requirement.specialConditions.length || '—'}</div>
              </div>
              <div>
                <div className="admission-metric-label">Документы</div>
                <div className="admission-metric-value">{requirement.documents.length || '—'}</div>
              </div>
            </div>
          </div>

          <div className="card admission-card">
            <div className="admission-section-header">
              <h3>Экзамены и минимальные баллы</h3>
              <span>необходимо подтвердить</span>
            </div>
            <div className="admission-subjects">
              {requirement.subjects.map((subject) => (
                <div key={`${requirement.programId}-${subject.subject}`} className="admission-subject">
                  <div>
                    <strong>{subject.subject}</strong>
                    <p>Минимум {subject.minScore} баллов</p>
                  </div>
                  <div className="admission-score">{subject.minScore}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="admission-grid">
          <div className="card admission-card">
            <div className="admission-section-header">
              <h3>Особые условия</h3>
              <span>льготы, квоты и преимущества</span>
            </div>
            {requirement.specialConditions.length ? (
              <div className="admission-chip-list">
                {requirement.specialConditions.map((condition) => (
                  <span key={condition} className="admission-chip">
                    {condition}
                  </span>
                ))}
              </div>
            ) : (
              <p className="admission-card-description">Для программы не предусмотрены дополнительные условия.</p>
            )}
          </div>

          <div className="card admission-card">
            <div className="admission-section-header">
              <h3>Документы для подачи</h3>
              <span>подготовьте заранее</span>
            </div>
            {requirement.documents.length ? (
              <ul className="admission-documents">
                {requirement.documents.map((document) => (
                  <li key={document}>{document}</li>
                ))}
              </ul>
            ) : (
              <p className="admission-card-description">Список документов уточняется в приёмной комиссии.</p>
            )}
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="app-container">
      <div className="container">{renderContent()}</div>
    </div>
  );
}


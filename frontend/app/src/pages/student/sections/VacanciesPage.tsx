import { useEffect, useMemo, useState } from 'react';
import { Briefcase, Clock3, Laptop, MapPin, ShieldCheck } from 'lucide-react';
import { getVacancies, submitVacancyApplication, type Vacancy } from '../../../api/careers';

export function VacanciesPage() {
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [vacancyStatus, setVacancyStatus] = useState<Record<string, 'idle' | 'submitting' | 'success'>>({});

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getVacancies();
        setVacancies(data);
      } catch (error) {
        console.error('Failed to load vacancies', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleVacancyApply = async (vacancyId: string) => {
    setVacancyStatus((prev) => ({ ...prev, [vacancyId]: 'submitting' }));
    try {
      await submitVacancyApplication({ vacancyId });
      setVacancyStatus((prev) => ({ ...prev, [vacancyId]: 'success' }));
    } catch (error) {
      console.error('Failed to submit vacancy application', error);
      setVacancyStatus((prev) => ({ ...prev, [vacancyId]: 'idle' }));
    }
  };

  const formatSalary = (salary?: Vacancy['salary']) => {
    if (!salary) {
      return null;
    }
    const from = salary.from ? salary.from.toLocaleString('ru-RU') : null;
    const to = salary.to ? salary.to.toLocaleString('ru-RU') : null;
    const currency = salary.currency ?? '₽';
    if (from && to) {
      return `${from} – ${to} ${currency}`;
    }
    if (from) {
      return `от ${from} ${currency}`;
    }
    if (to) {
      return `до ${to} ${currency}`;
    }
    return null;
  };

  const formatDate = (value?: string) => {
    if (!value) return null;
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return null;
    return new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long' }).format(date);
  };

  const skeletonCards = useMemo(
    () =>
      Array.from({ length: 3 }).map((_, index) => (
        <div className="card vacancy-card vacancy-card--skeleton" key={`vacancy-skeleton-${index}`}>
          <div className="skeleton-line" style={{ width: '60%' }} />
          <div className="skeleton-line" style={{ width: '40%' }} />
          <div className="skeleton-line" style={{ width: '90%', height: 12 }} />
          <div className="skeleton-line" style={{ width: '75%', height: 12 }} />
          <div className="skeleton-line" style={{ width: '55%', height: 12 }} />
        </div>
      )),
    [],
  );

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>Вакансии партнеров</h1>
            <p className="subtitle">Свежие позиции от компаний-менторов Макс Кэмпуса</p>
          </div>
        </div>
        {loading ? (
          <div className="vacancy-grid">{skeletonCards}</div>
        ) : vacancies.length === 0 ? (
          <div className="card-description">Нет доступных вакансий.</div>
        ) : (
          <div className="vacancy-grid">
            {vacancies.map((vacancy) => {
              const status = vacancyStatus[vacancy.id] ?? 'idle';
              const companyName = typeof vacancy.company === 'string' ? vacancy.company : vacancy.company?.name || 'Компания';
              const verified = typeof vacancy.company === 'object' && vacancy.company?.verified_partner;
              const locationStr =
                typeof vacancy.location === 'string'
                  ? vacancy.location
                  : `${vacancy.location?.city || ''}${vacancy.location?.city && vacancy.location?.country ? ', ' : ''}${vacancy.location?.country || ''}`.trim() ||
                    (vacancy.remote ? 'Удаленно' : 'Местоположение не указано');
              const directionStr = Array.isArray(vacancy.direction) ? vacancy.direction.join(', ') : vacancy.direction;
              const isRemote = vacancy.remote || (typeof vacancy.location === 'object' && vacancy.location?.type === 'remote');
              const salaryText = formatSalary(vacancy.salary);
              const postedAt = formatDate(vacancy.posted_at);
              const expiresAt = formatDate(vacancy.published_until);
              
              return (
                <div key={vacancy.id} className="card vacancy-card">
                  <div className="vacancy-card-header">
                    <div className="vacancy-card-title">
                      <div className="vacancy-company-line">
                        <span className="vacancy-company">{companyName}</span>
                        {verified && (
                          <span className="vacancy-badge">
                            <ShieldCheck size={14} />
                            Партнёр
                          </span>
                        )}
                      </div>
                      <h2>{vacancy.title}</h2>
                      <div className="vacancy-meta-line">
                        <span className="vacancy-meta">
                          <MapPin size={16} />
                          {locationStr}
                        </span>
                        {postedAt && (
                          <span className="vacancy-meta">
                            <Clock3 size={16} />
                            Опубликовано {postedAt}
                          </span>
                        )}
                        {expiresAt && (
                          <span className="vacancy-meta">
                            <Clock3 size={16} />
                            До {expiresAt}
                          </span>
                        )}
                      </div>
                    </div>
                    {salaryText && (
                      <div className="vacancy-salary">
                        <div className="vacancy-salary-label">Доход</div>
                        <div className="vacancy-salary-value">{salaryText}</div>
                        {vacancy.salary?.gross && <div className="vacancy-salary-note">до вычета</div>}
                      </div>
                    )}
                  </div>
                  <div className="vacancy-tags">
                    <span className="vacancy-tag vacancy-tag-strong">
                      <Briefcase size={14} />
                      {vacancy.grade}
                    </span>
                    {vacancy.employment && (
                      <span className="vacancy-tag">
                        <Clock3 size={14} />
                        {vacancy.employment}
                      </span>
                    )}
                    {isRemote && (
                      <span className="vacancy-tag vacancy-tag-remote">
                        <Laptop size={14} />
                        Удаленно
                      </span>
                    )}
                    {directionStr && <span className="vacancy-tag">{directionStr}</span>}
                  </div>
                  {vacancy.description && <p className="vacancy-description">{vacancy.description}</p>}
                  {vacancy.skills && vacancy.skills.length > 0 && (
                    <div className="vacancy-section">
                      <div className="vacancy-section-label">Навыки</div>
                      <div className="vacancy-chip-row">
                        {vacancy.skills.map((skill) => (
                          <span key={skill} className="vacancy-chip">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {Array.isArray(vacancy.benefits) && vacancy.benefits.length > 0 && (
                    <div className="vacancy-section">
                      <div className="vacancy-section-label">Преимущества</div>
                      <ul className="vacancy-benefits">
                        {vacancy.benefits.map((benefit) => (
                          <li key={benefit}>{benefit}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <button
                    className="btn vacancy-apply-btn"
                    type="button"
                    onClick={() => handleVacancyApply(vacancy.id)}
                    disabled={status === 'submitting'}
                  >
                    {status === 'success'
                      ? 'Отклик отправлен'
                      : status === 'submitting'
                        ? 'Отправляем...'
                        : 'Откликнуться'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}


import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../../../context/AppStateContext';
import {
  getAdmissionsPrograms,
  getOpenDays,
  type AdmissionsProgram,
  type OpenDayEvent,
} from '../../../api/admissions';

const FALLBACK_POSTER =
  'data:image/svg+xml;charset=UTF-8,' +
  encodeURIComponent(
    `<svg width="640" height="360" xmlns="http://www.w3.org/2000/svg">
      <rect width="640" height="360" fill="#F0F4FF" />
      <path d="M80 280h120l-40-80 40-80h-80l-40 80 40 80z" fill="#D6E0FF" />
      <circle cx="420" cy="180" r="90" fill="#E2E9FF" />
      <text x="50%" y="50%" text-anchor="middle" fill="#8EA2FF" font-family="Inter, Arial" font-size="28" letter-spacing="0.2em">MAX</text>
    </svg>`,
  );

const TYPE_LABELS: Record<string, string> = {
  open_day: 'День открытых дверей',
  excursion: 'Экскурсия',
  webinar: 'Вебинар',
};

function formatEventType(type?: string) {
  if (!type) return 'Мероприятие';
  return TYPE_LABELS[type] ?? type;
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
  });
}

function formatTime(date?: string) {
  if (!date) return 'время уточняется';
  return new Date(date).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function OpenDayPage() {
  const { selectedUniversityId } = useAppState();
  const navigate = useNavigate();
  const [, setPrograms] = useState<AdmissionsProgram[]>([]);
  const [events, setEvents] = useState<OpenDayEvent[]>([]);
  const [filters, setFilters] = useState<{ cities: string[]; types: string[] }>({ cities: [], types: [] });
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [city, setCity] = useState('all');
  const [type, setType] = useState('all');

  useEffect(() => {
    if (!selectedUniversityId) {
      navigate('/');
      return;
    }

    let mounted = true;

    const load = async () => {
      setLoading(true);
      setErrorMessage(null);
      try {
        const [{ programs: programsResponse }, openDaysResponse] = await Promise.all([
          getAdmissionsPrograms(selectedUniversityId),
          getOpenDays(selectedUniversityId),
        ]);

        if (!mounted) {
          return;
        }

        setPrograms(programsResponse);
        setEvents(openDaysResponse.events);
        setFilters(openDaysResponse.filters);
      } catch (loadError) {
        console.error('Failed to load open days data', loadError);
        if (mounted) {
          setErrorMessage('Не удалось загрузить мероприятия.');
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

  const filteredEvents = useMemo(() => {
    return events.filter((event) => {
      const matchesCity = city === 'all' || event.city === city;
      const matchesType = type === 'all' || event.type === type;
      return matchesCity && matchesType;
    });
  }, [events, city, type]);

  const stats = useMemo(() => {
    const upcoming = filteredEvents.length;
    const totalCapacity = filteredEvents.reduce((sum, event) => sum + (event.capacity ?? 0), 0);
    const openCount = filteredEvents.filter((event) => event.registrationOpen).length;
    return {
      upcoming,
      totalCapacity,
      openCount,
    };
  }, [filteredEvents]);

  const renderSkeleton = () => (
    <div className="open-day-grid">
      {Array.from({ length: 2 }).map((_, index) => (
        <div key={`open-day-skeleton-${index}`} className="open-day-card open-day-card--skeleton">
          <div className="open-day-card-poster skeleton-block" />
          <div className="open-day-card-body">
            <div className="skeleton-line" style={{ width: '60%' }} />
            <div className="skeleton-line" style={{ width: '40%' }} />
            <div className="skeleton-line" style={{ width: '80%' }} />
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
            <h1>Дни открытых дверей</h1>
            <p className="subtitle">Выберите город или формат и зарегистрируйтесь на ближайшее мероприятие кампуса MAX.</p>
          </div>
        </div>

        {loading ? (
          renderSkeleton()
        ) : errorMessage && events.length === 0 ? (
          <div className="card">
            <div className="card-title">Ошибка</div>
            <div className="card-description">{errorMessage}</div>
          </div>
        ) : (
          <>
            <div className="open-day-stats">
              <div className="open-day-stat-card">
                <div className="open-day-stat-label">Запланировано</div>
                <div className="open-day-stat-value">{stats.upcoming}</div>
              </div>
              <div className="open-day-stat-card">
                <div className="open-day-stat-label">Мест</div>
                <div className="open-day-stat-value">{stats.totalCapacity}</div>
              </div>
              <div className="open-day-stat-card">
                <div className="open-day-stat-label">С открытой регистрацией</div>
                <div className="open-day-stat-value">{stats.openCount}</div>
              </div>
            </div>

            <div className="open-day-toolbar">
              <select className="form-input" value={city} onChange={(event) => setCity(event.target.value)}>
                <option value="all">Все города</option>
                {filters.cities.map((cityOption) => (
                  <option key={cityOption} value={cityOption}>
                    {cityOption}
                  </option>
                ))}
              </select>
              <select className="form-input" value={type} onChange={(event) => setType(event.target.value)}>
                <option value="all">Все форматы</option>
                {filters.types.map((typeOption) => (
                  <option key={typeOption} value={typeOption}>
                    {formatEventType(typeOption)}
                  </option>
                ))}
              </select>
            </div>

            {filteredEvents.length === 0 ? (
              <div className="card">
                <div className="card-title">Мероприятия не найдены</div>
                <div className="card-description">Попробуйте выбрать другой город или формат.</div>
              </div>
            ) : (
              <div className="open-day-grid">
                {filteredEvents.map((eventItem) => {
                  const poster =
                    eventItem.media?.posterUrl && !eventItem.media.posterUrl.includes('example.com')
                      ? eventItem.media.posterUrl
                      : FALLBACK_POSTER;
                  const remaining =
                    typeof eventItem.remaining === 'number'
                      ? eventItem.remaining
                      : typeof eventItem.capacity === 'number' && typeof eventItem.registered === 'number'
                        ? Math.max(eventItem.capacity - eventItem.registered, 0)
                        : null;
                  return (
                    <div key={eventItem.id} className="open-day-card card">
                      <div className="open-day-card-poster" style={{ backgroundImage: `url(${poster})` }} aria-hidden="true" />
                      <div className="open-day-card-body">
                        <div className="open-day-card-tags">
                          <span className="open-day-chip">{formatEventType(eventItem.type)}</span>
                          {eventItem.city && <span className="open-day-chip open-day-chip--ghost">{eventItem.city}</span>}
                        </div>
                        <h2>{eventItem.title ?? 'День открытых дверей'}</h2>
                        {eventItem.description && <p className="open-day-description">{eventItem.description}</p>}

                        <div className="open-day-meta">
                          <span>
                            {formatDate(eventItem.date)} • {formatTime(eventItem.startsAt ?? eventItem.time)}
                          </span>
                          <span>{eventItem.location ?? 'Локация уточняется'}</span>
                          {eventItem.registrationDeadline && (
                            <span>Регистрация до {formatDate(eventItem.registrationDeadline)}</span>
                          )}
                          {eventItem.contacts?.email && <span>Контакт: {eventItem.contacts.email}</span>}
                        </div>

                        {eventItem.programs && eventItem.programs.length ? (
                          <div className="open-day-programs">
                            <div className="open-day-section-label">Программы</div>
                            <div className="open-day-chip-row">
                              {eventItem.programs.map((program) => (
                                <span key={program.id} className="open-day-chip open-day-chip--ghost">
                                  {program.title}
                                </span>
                              ))}
                            </div>
                          </div>
                        ) : null}

                        <div className="open-day-card-footer">
                          <div>
                            <span className="open-day-card-footer-label">Свободных мест</span>
                            <div className="open-day-card-footer-value">
                              {typeof remaining === 'number' ? remaining : eventItem.capacity ?? '—'}
                            </div>
                          </div>
                          {eventItem.registrationLink ? (
                            <a
                              href={eventItem.registrationLink}
                              className="btn open-day-link-btn"
                              target="_blank"
                              rel="noreferrer"
                              aria-label="Перейти на страницу регистрации"
                            >
                              Зарегистрироваться
                            </a>
                          ) : (
                            <button className="btn open-day-link-btn" type="button" disabled={!eventItem.registrationOpen}>
                              {eventItem.registrationOpen ? 'Регистрация' : 'Скоро откроется'}
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


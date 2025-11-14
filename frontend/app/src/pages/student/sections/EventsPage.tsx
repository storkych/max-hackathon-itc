import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { CalendarClock, MapPin, Ticket, Users } from 'lucide-react';
import { getEvents as getEventsData, submitEventRegistration, type Event } from '../../../api/events';

const FALLBACK_EVENT_POSTER =
  'data:image/svg+xml;charset=UTF-8,' +
  encodeURIComponent(
    `<svg width="320" height="180" xmlns="http://www.w3.org/2000/svg">
      <rect width="320" height="180" rx="16" fill="#E9ECEF"/>
      <text x="50%" y="50%" text-anchor="middle" fill="#ADB5BD" font-family="Arial" font-size="20">MAX</text>
    </svg>`,
  );

const VISIBILITY_LABELS: Record<string, string> = {
  public: 'Открыто',
  students_only: 'Только студенты',
  staff_only: 'Только сотрудники',
  invite_only: 'По приглашению',
};

const STATUS_LABELS: Record<string, string> = {
  scheduled: 'Запланировано',
  cancelled: 'Отменено',
  completed: 'Завершено',
  draft: 'Черновик',
};

function getPosterSrc(src?: string | null) {
  if (!src) {
    return FALLBACK_EVENT_POSTER;
  }
  if (src.includes('example.com')) {
    return FALLBACK_EVENT_POSTER;
  }
  return src;
}

export function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [registrationStatus, setRegistrationStatus] = useState<Record<string, 'idle' | 'submitting' | 'success'>>({});

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getEventsData();
        setEvents(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Failed to load events', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const dateFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat('ru-RU', {
        day: 'numeric',
        month: 'long',
      }),
    [],
  );

  const timeFormatter = useMemo(
    () =>
      new Intl.DateTimeFormat('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    [],
  );

  const formatDateRange = (eventItem: Event) => {
    if (!eventItem.starts_at) {
      return null;
    }
    const start = new Date(eventItem.starts_at);
    const end = eventItem.ends_at ? new Date(eventItem.ends_at) : null;
    if (!end) {
      return `${dateFormatter.format(start)}, ${timeFormatter.format(start)}`;
    }
    const sameDay =
      start.getFullYear() === end.getFullYear() &&
      start.getMonth() === end.getMonth() &&
      start.getDate() === end.getDate();
    if (sameDay) {
      return `${dateFormatter.format(start)}, ${timeFormatter.format(start)} – ${timeFormatter.format(end)}`;
    }
    return `${dateFormatter.format(start)} ${timeFormatter.format(start)} — ${dateFormatter.format(end)} ${timeFormatter.format(end)}`;
  };

  const handleEventRegistration = async (formEvent: FormEvent<HTMLFormElement>, eventId: string) => {
    formEvent.preventDefault();
    const formData = new FormData(formEvent.currentTarget);
    const guests = Number(formData.get('guests')) || 1;
    const comment = (formData.get('comment') as string) || '';
    setRegistrationStatus((prev) => ({ ...prev, [eventId]: 'submitting' }));
    try {
      await submitEventRegistration({
        eventId,
        formPayload: {
          guests,
          comment,
        },
      });
      const next = await getEventsData();
      setEvents(Array.isArray(next) ? next : []);
      setRegistrationStatus((prev) => ({ ...prev, [eventId]: 'success' }));
      formEvent.currentTarget.reset();
    } catch (error) {
      console.error('Failed to register for event', error);
      setRegistrationStatus((prev) => ({ ...prev, [eventId]: 'idle' }));
    }
  };

  if (loading) {
    return (
      <div className="app-container">
        <div className="container">
          <div className="card-description">Загрузка событий...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="container">
        <div className="page-heading">
          <div>
            <h1>События и встречи</h1>
            <p className="subtitle">Регулярные митапы, хакатоны и карьерные активности от сообщества MAX</p>
          </div>
        </div>
        {loading ? (
          <div className="events-grid">
            {Array.from({ length: 2 }).map((_, index) => (
              <div key={`event-skeleton-${index}`} className="card event-card event-card--skeleton">
                <div className="skeleton-line" style={{ width: '70%' }} />
                <div className="skeleton-line" style={{ width: '40%' }} />
                <div className="skeleton-line" style={{ width: '85%', height: 12 }} />
                <div className="skeleton-line" style={{ width: '65%', height: 12 }} />
              </div>
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="card-description">Нет доступных событий.</div>
        ) : (
          <div className="events-grid">
            {events.map((eventItem) => {
              const status = registrationStatus[eventItem.id] ?? 'idle';
              const dateLabel = formatDateRange(eventItem);
              const visibilityLabel = eventItem.visibility ? VISIBILITY_LABELS[eventItem.visibility] ?? eventItem.visibility : null;
              const statusLabel = eventItem.status ? STATUS_LABELS[eventItem.status] ?? eventItem.status : null;
              return (
                <div key={eventItem.id} className="card event-card">
                  <div className="event-cover">
                    <img
                      src={getPosterSrc(eventItem.cover)}
                      alt={eventItem.title}
                      onError={(e) => {
                        if (e.currentTarget.src !== FALLBACK_EVENT_POSTER) {
                          e.currentTarget.src = FALLBACK_EVENT_POSTER;
                        }
                      }}
                    />
                  </div>
                  <div className="event-card-body">
                    <div className="event-card-header">
                      <div>
                        <div className="event-category">{eventItem.category}</div>
                        <h2>{eventItem.title}</h2>
                        {eventItem.subtitle && <p className="event-subtitle">{eventItem.subtitle}</p>}
                      </div>
                      <div className="event-badges">
                        {visibilityLabel && <span className="event-badge">{visibilityLabel}</span>}
                        {statusLabel && (
                          <span className={`event-badge event-badge--${eventItem.status}`}>{statusLabel}</span>
                        )}
                      </div>
                    </div>

                    <div className="event-meta">
                      {dateLabel && (
                        <div className="event-meta-item">
                          <CalendarClock size={16} />
                          <span>{dateLabel}</span>
                        </div>
                      )}
                      {eventItem.location && (
                        <div className="event-meta-item">
                          <MapPin size={16} />
                          <span>{eventItem.location}</span>
                        </div>
                      )}
                      {typeof eventItem.capacity === 'number' && (
                        <div className="event-meta-item">
                          <Users size={16} />
                          <span>
                            {eventItem.remaining ?? eventItem.capacity} из {eventItem.capacity} мест
                          </span>
                        </div>
                      )}
                      {eventItem.registration_deadline && (
                        <div className="event-meta-item">
                          <Ticket size={16} />
                          <span>
                            Регистрация до {dateFormatter.format(new Date(eventItem.registration_deadline))}
                          </span>
                        </div>
                      )}
                    </div>

                    {eventItem.tags && eventItem.tags.length > 0 && (
                      <div className="event-tags">
                        {eventItem.tags.map((tag) => (
                          <span key={tag} className="event-tag">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {eventItem.description && <p className="event-description">{eventItem.description}</p>}

                    {eventItem.agenda && eventItem.agenda.length > 0 && (
                      <div className="event-section">
                        <div className="event-section-title">Программа</div>
                        <ul className="event-agenda">
                          {eventItem.agenda.map((item, index) => (
                            <li key={`${eventItem.id}-agenda-${index}`}>
                              {item.time && <span className="event-agenda-time">{item.time}</span>}
                              <span>{item.title}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <form className="event-register-form" onSubmit={(e) => handleEventRegistration(e, eventItem.id)}>
                      <input type="hidden" name="event_id" value={eventItem.id} />
                      <div className="form-group-inline">
                        <label className="form-label" htmlFor={`guests-${eventItem.id}`}>
                          Гостей
                        </label>
                        <input
                          className="form-input"
                          id={`guests-${eventItem.id}`}
                          name="guests"
                          type="number"
                          min={1}
                          max={eventItem.remaining ?? eventItem.capacity ?? 10}
                          defaultValue={1}
                        />
                      </div>
                      <div className="form-group">
                        <label className="form-label" htmlFor={`comment-${eventItem.id}`}>
                          Комментарий
                        </label>
                        <textarea
                          className="form-input"
                          id={`comment-${eventItem.id}`}
                          name="comment"
                          placeholder="Например: Буду вовремя"
                          rows={2}
                        />
                      </div>
                      <button className="btn event-register-btn" type="submit" disabled={status === 'submitting'}>
                        {status === 'success' ? 'Заявка отправлена' : status === 'submitting' ? 'Отправляем...' : 'Оставить заявку'}
                      </button>
                    </form>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}


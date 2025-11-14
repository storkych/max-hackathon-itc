import { useEffect, useMemo, useRef, useState } from 'react';
import type { FormEvent, TouchEvent } from 'react';
import { Pencil } from 'lucide-react';
import { getMySchedule, type ScheduleItem } from '../../../api/schedule';

const DEFAULT_GROUP_ID = 'group-msu-phys-101';
const GROUP_STORAGE_KEY = 'student_schedule_group_id';

const timeFormatter = new Intl.DateTimeFormat('ru-RU', {
  hour: '2-digit',
  minute: '2-digit',
});

const weekdayFormatter = new Intl.DateTimeFormat('ru-RU', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
});

const weekdayShortFormatter = new Intl.DateTimeFormat('ru-RU', {
  weekday: 'short',
});

const monthFormatter = new Intl.DateTimeFormat('ru-RU', {
  month: 'long',
});

const LESSON_TYPE_META: Record<
  string,
  {
    label: string;
    tone: 'blue' | 'green' | 'orange' | 'purple' | 'gray';
  }
> = {
  lecture: { label: 'Лекция', tone: 'blue' },
  practice: { label: 'Практика', tone: 'green' },
  seminar: { label: 'Семинар', tone: 'orange' },
  lab: { label: 'Лабораторная', tone: 'purple' },
};

const FORMAT_LABELS: Record<string, string> = {
  offline: 'Очное',
  online: 'Онлайн',
  hybrid: 'Гибрид',
};

type ScheduleLessonView = ScheduleItem & {
  startDate: Date;
  endDate: Date;
  dayKey: string;
  startLabel: string;
  endLabel: string;
};

interface ScheduleDay {
  date: Date;
  key: string;
  lessons: ScheduleLessonView[];
  isToday: boolean;
}

function getMonday(date: Date) {
  const result = new Date(date);
  result.setHours(0, 0, 0, 0);
  const day = result.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  result.setDate(result.getDate() + diff);
  return result;
}

function addDays(date: Date, days: number) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function formatDateParam(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function isSameDay(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

function formatWeekRange(start: Date, end: Date) {
  const sameMonth = start.getMonth() === end.getMonth();
  const startDay = start.getDate();
  const endDay = end.getDate();
  const startMonth = monthFormatter.format(start);
  const endMonth = monthFormatter.format(end);
  const yearLabel = start.getFullYear() === end.getFullYear() ? start.getFullYear() : `${start.getFullYear()}–${end.getFullYear()}`;

  if (sameMonth) {
    return `${startDay}–${endDay} ${startMonth} ${start.getFullYear()}`;
  }

  return `${startDay} ${startMonth} – ${endDay} ${endMonth} ${yearLabel}`;
}

function getTodayKey() {
  return formatDateParam(new Date());
}

function formatLessonCount(count: number) {
  if (count === 0) {
    return 'Выходной';
  }
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;
  if (lastDigit === 1 && lastTwoDigits !== 11) {
    return `${count} занятие`;
  }
  if ([2, 3, 4].includes(lastDigit) && ![12, 13, 14].includes(lastTwoDigits)) {
    return `${count} занятия`;
  }
  return `${count} занятий`;
}

function loadStoredGroupId() {
  if (typeof window === 'undefined') {
    return DEFAULT_GROUP_ID;
  }
  try {
    return window.localStorage.getItem(GROUP_STORAGE_KEY) ?? DEFAULT_GROUP_ID;
  } catch (error) {
    console.warn('Failed to load stored schedule group id', error);
    return DEFAULT_GROUP_ID;
  }
}

export function SchedulePage() {
  const [weekStart, setWeekStart] = useState<Date>(() => getMonday(new Date()));
  const [groupInput, setGroupInput] = useState<string>(() => loadStoredGroupId());
  const [activeGroupId, setActiveGroupId] = useState<string>(() => loadStoredGroupId());
  const [lessons, setLessons] = useState<ScheduleLessonView[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [, setMetaRange] = useState<{ from?: string; to?: string; time_zone?: string }>({});
  const [metaGroup, setMetaGroup] = useState<{ id?: string; name?: string }>({});
  const [activeDayKey, setActiveDayKey] = useState<string>(() => getTodayKey());
  const swipeStartX = useRef<number | null>(null);
  const swipeDeltaX = useRef(0);
  const tabsWrapperRef = useRef<HTMLDivElement | null>(null);
  const swipeAnimationTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [swipeOffset, setSwipeOffset] = useState(0);
  const [isSwipeAnimating, setIsSwipeAnimating] = useState(false);
  const swipeLockedRef = useRef(false);
  const [isEditingGroup, setIsEditingGroup] = useState(false);

  const weekEnd = useMemo(() => addDays(weekStart, 6), [weekStart]);
  const isCurrentWeek = isSameDay(weekStart, getMonday(new Date()));

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      window.localStorage.setItem(GROUP_STORAGE_KEY, groupInput);
    } catch (storageError) {
      console.warn('Failed to persist schedule group id', storageError);
    }
  }, [groupInput]);

  useEffect(() => {
    let cancelled = false;

    const loadSchedule = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getMySchedule({
          from: formatDateParam(weekStart),
          to: formatDateParam(weekEnd),
          groupId: activeGroupId,
        });

        if (cancelled) {
          return;
        }

        const items = Array.isArray(response.items) ? response.items : [];
        const normalized: ScheduleLessonView[] = items.map((item) => {
          const startDate = new Date(item.starts_at);
          const endDate = new Date(item.ends_at);
          return {
            ...item,
            startDate,
            endDate,
            dayKey: formatDateParam(startDate),
            startLabel: timeFormatter.format(startDate),
            endLabel: timeFormatter.format(endDate),
          };
        });

        setLessons(normalized);
        setMetaRange(response.range ?? {});
        setMetaGroup(response.group ?? {});
      } catch (err) {
        if (cancelled) {
          return;
        }
        console.error('Failed to load schedule', err);
        setLessons([]);
        setError('Не удалось загрузить расписание. Попробуйте обновить страницу или выбрать другую группу.');
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadSchedule();

    return () => {
      cancelled = true;
    };
  }, [weekStart, weekEnd, activeGroupId]);

  const weekDays: ScheduleDay[] = useMemo(() => {
    return Array.from({ length: 7 }).map((_, index) => {
      const date = addDays(weekStart, index);
      const key = formatDateParam(date);
      const dayLessons = lessons
        .filter((lesson) => lesson.dayKey === key)
        .sort((a, b) => a.startDate.getTime() - b.startDate.getTime());

      return {
        date,
        key,
        lessons: dayLessons,
        isToday: isSameDay(date, new Date()),
      };
    });
  }, [weekStart, lessons]);

  useEffect(() => {
    if (!weekDays.length) {
      return;
    }
    setActiveDayKey((prev) => {
      if (weekDays.some((day) => day.key === prev)) {
        return prev;
      }
      const todayKey = getTodayKey();
      const todayInWeek = weekDays.find((day) => day.key === todayKey);
      return todayInWeek?.key ?? weekDays[0].key;
    });
  }, [weekDays]);

  const rangeLabel = useMemo(() => formatWeekRange(weekStart, weekEnd), [weekStart, weekEnd]);

  const activeDay = useMemo(() => weekDays.find((day) => day.key === activeDayKey) ?? weekDays[0], [weekDays, activeDayKey]);
  const activeLessons = activeDay?.lessons ?? [];

  const handleGroupSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!groupInput.trim()) {
      return;
    }
    setActiveGroupId(groupInput.trim());
    setIsEditingGroup(false);
  };

  const handlePrevWeek = () => setWeekStart((prev) => addDays(prev, -7));
  const handleNextWeek = () => setWeekStart((prev) => addDays(prev, 7));
  const handleResetWeek = () => {
    const monday = getMonday(new Date());
    setWeekStart(monday);
    setActiveDayKey(getTodayKey());
    setSwipeOffset(0);
    setIsSwipeAnimating(false);
  };

  const clearSwipeAnimationTimeout = () => {
    if (swipeAnimationTimeoutRef.current) {
      clearTimeout(swipeAnimationTimeoutRef.current);
      swipeAnimationTimeoutRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      clearSwipeAnimationTimeout();
    };
  }, []);

  const getTabsWidth = () => tabsWrapperRef.current?.offsetWidth ?? window.innerWidth ?? 320;

  const revertSwipePosition = () => {
    setIsSwipeAnimating(true);
    setSwipeOffset(0);
    clearSwipeAnimationTimeout();
    swipeAnimationTimeoutRef.current = window.setTimeout(() => {
      setIsSwipeAnimating(false);
    }, 240);
  };

  const performWeekSwipe = (direction: 1 | -1) => {
    const width = getTabsWidth();
    swipeLockedRef.current = true;
    setIsSwipeAnimating(true);
    setSwipeOffset(direction * width);

    clearSwipeAnimationTimeout();
    swipeAnimationTimeoutRef.current = window.setTimeout(() => {
      if (direction > 0) {
        handlePrevWeek();
      } else {
        handleNextWeek();
      }

      setIsSwipeAnimating(false);
      setSwipeOffset(-direction * width);

      requestAnimationFrame(() => {
        setIsSwipeAnimating(true);
        setSwipeOffset(0);
        clearSwipeAnimationTimeout();
        swipeAnimationTimeoutRef.current = window.setTimeout(() => {
          setIsSwipeAnimating(false);
          swipeLockedRef.current = false;
        }, 240);
      });
    }, 220);
  };

  const handleSwipeStart = (event: TouchEvent<HTMLDivElement>) => {
    if (swipeLockedRef.current || event.touches.length !== 1) {
      return;
    }
    swipeStartX.current = event.touches[0].clientX;
    swipeDeltaX.current = 0;
    setIsSwipeAnimating(false);
  };

  const handleSwipeMove = (event: TouchEvent<HTMLDivElement>) => {
    if (swipeStartX.current === null || event.touches.length !== 1 || swipeLockedRef.current) {
      return;
    }
    const deltaX = event.touches[0].clientX - swipeStartX.current;
    swipeDeltaX.current = deltaX;
    setSwipeOffset(deltaX);
  };

  const handleSwipeEnd = () => {
    if (swipeStartX.current === null || swipeLockedRef.current) {
      return;
    }
    const deltaX = swipeDeltaX.current;
    swipeStartX.current = null;
    swipeDeltaX.current = 0;
    const threshold = 60;
    if (deltaX > threshold) {
      performWeekSwipe(1);
    } else if (deltaX < -threshold) {
      performWeekSwipe(-1);
    } else {
      revertSwipePosition();
    }
  };

  const renderSkeleton = () => (
    <div className="schedule-grid">
      {Array.from({ length: 3 }).map((_, index) => (
        <div key={index} className="card schedule-day-card schedule-day-card--skeleton">
          <div className="schedule-day-header">
            <div className="skeleton-line" style={{ width: '60%' }} />
            <div className="skeleton-line" style={{ width: 80 }} />
          </div>
          <div className="schedule-lesson schedule-lesson--skeleton">
            <div className="skeleton-line" style={{ width: 56, height: 14 }} />
            <div className="skeleton-line" style={{ width: '70%' }} />
            <div className="skeleton-line" style={{ width: '50%' }} />
          </div>
          <div className="schedule-lesson schedule-lesson--skeleton">
            <div className="skeleton-line" style={{ width: 56, height: 14 }} />
            <div className="skeleton-line" style={{ width: '65%' }} />
            <div className="skeleton-line" style={{ width: '45%' }} />
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="app-container">
      <div className="container">
        {isEditingGroup && (
          <div className="card schedule-card">
            <form className="schedule-group-form" onSubmit={handleGroupSubmit}>
              <label htmlFor="groupId" className="form-label">
                Группа / поток
              </label>
              <div className="schedule-group-input">
                <input
                  id="groupId"
                  className="form-input"
                  value={groupInput}
                  onChange={(event) => setGroupInput(event.target.value)}
                  placeholder="group-msu-phys-101"
                />
                <button className="btn" type="submit" disabled={loading}>
                  Обновить
                </button>
              </div>
            </form>
          </div>
        )}

        {error && (
          <div className="card" style={{ marginBottom: 16, borderColor: 'var(--danger)', color: 'var(--danger)' }}>
            {error}
          </div>
        )}

        <div className="schedule-group-display">
          <div className="schedule-group-info">
            <div className="schedule-group-label">Группа</div>
            <div className="schedule-group-name">{metaGroup?.name ?? activeGroupId}</div>
          </div>
          <button
            type="button"
            className="schedule-group-edit"
            onClick={() => setIsEditingGroup((prev) => !prev)}
            aria-label="Изменить группу"
          >
            <Pencil size={18} />
          </button>
        </div>

        {loading ? (
          renderSkeleton()
        ) : weekDays.length === 0 ? (
          <div className="card" style={{ marginTop: 16 }}>
            <div className="card-description">Расписание не найдено для выбранного диапазона.</div>
          </div>
        ) : (
          <>
            <div className="schedule-tabs-bar">
              <div
                className="schedule-day-tabs-wrapper"
                ref={tabsWrapperRef}
                onTouchStart={handleSwipeStart}
                onTouchMove={handleSwipeMove}
                onTouchEnd={handleSwipeEnd}
              >
                <div
                  className="schedule-day-tabs"
                  style={{
                    transform: `translateX(${swipeOffset}px)`,
                    transition: isSwipeAnimating ? 'transform 0.24s ease' : 'none',
                  }}
                >
                  {weekDays.map((day) => (
                    <button
                      key={day.key}
                      type="button"
                      className={`schedule-day-tab${day.key === activeDayKey ? ' schedule-day-tab--active' : ''}`}
                      onClick={() => setActiveDayKey(day.key)}
                    >
                      <span className="schedule-day-tab-weekday">
                        {weekdayShortFormatter.format(day.date).replace('.', '').toUpperCase()}
                      </span>
                      <span className="schedule-day-tab-date">{day.date.getDate()}</span>
                      {day.lessons.length > 0 && (
                        <span className="schedule-day-tab-count">{formatLessonCount(day.lessons.length)}</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="schedule-tabs-secondary">
              <button
                type="button"
                className="btn btn-secondary btn-ghost schedule-today-btn"
                onClick={handleResetWeek}
                disabled={isCurrentWeek && activeDay?.isToday}
              >
                Сегодня
              </button>
              <div className="schedule-tabs-range">{rangeLabel}</div>
            </div>

            <div className={`card schedule-day-card${activeDay?.isToday ? ' schedule-day-card--today' : ''}`}>
              <div className="schedule-day-header">
                <div>
                  <div className="schedule-day-title">{activeDay ? weekdayFormatter.format(activeDay.date) : 'День не выбран'}</div>
                  <div className="schedule-day-count">{formatLessonCount(activeLessons.length)}</div>
                </div>
              </div>

              {activeLessons.length === 0 ? (
                <div className="schedule-day-empty">Нет занятий</div>
              ) : (
                <div className="schedule-lessons">
                  {activeLessons.map((lesson) => {
                    const lessonMeta =
                      LESSON_TYPE_META[lesson.lesson_type ?? ''] ?? { label: lesson.lesson_type ?? 'Занятие', tone: 'gray' };
                    const formatLabel = FORMAT_LABELS[lesson.format ?? ''] ?? lesson.format ?? 'Формат не указан';

                    return (
                      <div key={lesson.id} className="schedule-lesson">
                        <div className="schedule-lesson-time">
                          <span>{lesson.startLabel}</span>
                          <span className="schedule-lesson-time-divider" />
                          <span>{lesson.endLabel}</span>
                        </div>
                        <div className="schedule-lesson-body">
                          <div className="schedule-lesson-subject">{lesson.subject}</div>
                          <div className="schedule-lesson-tags">
                            <span className={`lesson-type-badge lesson-type-badge--${lessonMeta.tone}`}>{lessonMeta.label}</span>
                            <span className="lesson-format-pill">{formatLabel}</span>
                          </div>
                          {lesson.room?.name && (
                            <div className="schedule-lesson-meta">
                              <span>{lesson.room.name}</span>
                              {lesson.room.campus && <span> · {lesson.room.campus}</span>}
                            </div>
                          )}
                          {lesson.teacher?.full_name && <div className="schedule-lesson-meta">{lesson.teacher.full_name}</div>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}


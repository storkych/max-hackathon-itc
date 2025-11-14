import type { BottomNavButton } from '../api/settings';
import type { UserRole } from '../context/AppStateContext';

const STUDENT_PUBLIC_SECTION_IDS = ['schedule', 'task-tracker', 'events', 'vacancies'];

const BASE_AVAILABLE_BUTTONS: Record<UserRole, BottomNavButton[]> = {
  abiturient: [
    { id: 'programs', label: 'Программы', icon: 'programs', route: '/dashboard/abiturient/programs' },
    { id: 'admission-conditions', label: 'Условия поступления', icon: 'admission-conditions', route: '/dashboard/abiturient/admission-conditions' },
    { id: 'open-day', label: 'Дни открытых дверей', icon: 'open-day', route: '/dashboard/abiturient/open-day' },
    { id: 'inquiry', label: 'Вопрос', icon: 'admission-inquiry', route: '/dashboard/abiturient/admission-inquiry' },
  ],
  student: [
    { id: 'schedule', label: 'Расписание', icon: 'schedule', route: '/dashboard/student/schedule' },
    { id: 'task-tracker', label: 'Таск-трекер', icon: 'task-tracker', route: '/dashboard/student/task-tracker' },
    { id: 'events', label: 'События кампуса', icon: 'events', route: '/dashboard/student/events' },
    { id: 'vacancies', label: 'Вакансии партнеров', icon: 'vacancies', route: '/dashboard/student/vacancies' },
    { id: 'projects', label: 'Проекты', icon: 'projects', route: '/dashboard/student/projects' },
    { id: 'career', label: 'Карьера и консультации', icon: 'career', route: '/dashboard/student/career' },
    { id: 'deanery', label: 'Деканат', icon: 'deanery', route: '/dashboard/student/deanery' },
    { id: 'dormitory', label: 'Общежитие', icon: 'dormitory', route: '/dashboard/student/dormitory' },
    { id: 'library', label: 'Библиотека', icon: 'library', route: '/dashboard/student/library' },
  ],
  staff: [
    { id: 'travel', label: 'Командировки', icon: 'business-trips', route: '/dashboard/staff/travel' },
    { id: 'vacations', label: 'Отпуска', icon: 'vacations', route: '/dashboard/staff/vacations' },
    { id: 'office', label: 'Офис и HR', icon: 'office', route: '/dashboard/staff/office' },
  ],
  admin: [
    { id: 'campus', label: 'Управление', icon: 'campus-management', route: '/dashboard/admin' },
    { id: 'metrics', label: 'Метрики', icon: 'academic-metrics', route: '/dashboard/admin' },
    { id: 'news', label: 'Новости', icon: 'news-aggregator', route: '/dashboard/admin' },
  ],
};

export interface BottomNavAvailabilityOptions {
  isStudentAuthenticated?: boolean;
}

export function getAvailableBottomNavButtons(
  role: UserRole,
  options: BottomNavAvailabilityOptions = {},
): BottomNavButton[] {
  const baseButtons = BASE_AVAILABLE_BUTTONS[role] ?? [];

  if (role === 'student') {
    const isAuthenticated = options.isStudentAuthenticated ?? true;
    if (!isAuthenticated) {
      return baseButtons.filter((button) => STUDENT_PUBLIC_SECTION_IDS.includes(button.id));
    }
  }

  return baseButtons;
}

export function filterButtonsForRole(
  buttons: BottomNavButton[],
  role: UserRole,
  options: BottomNavAvailabilityOptions = {},
): BottomNavButton[] {
  const allowedIds = new Set(getAvailableBottomNavButtons(role, options).map((button) => button.id));
  // Если нет ограничений (например, роль не найдена), возвращаем исходные кнопки
  if (allowedIds.size === 0) {
    return buttons;
  }
  return buttons.filter((button) => allowedIds.has(button.id));
}


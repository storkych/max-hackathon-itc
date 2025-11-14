import type { BottomNavButton } from '../api/settings';
import type { UserRole } from '../context/AppStateContext';

export function getDefaultBottomNavButtons(role: UserRole): BottomNavButton[] {
  // Возвращаем только выбранные кнопки (без "Главная" и "Настройки", они фиксированные)
  switch (role) {
    case 'abiturient':
      return [
        {
          id: 'programs',
          label: 'Программы',
          icon: 'programs',
          route: '/dashboard/abiturient/programs',
          color: '#0077FF',
        },
        {
          id: 'open-day',
          label: 'Дни открытых дверей',
          icon: 'open-day',
          route: '/dashboard/abiturient/open-day',
          color: '#0077FF',
        },
      ];

    case 'student':
      return [
        {
          id: 'schedule',
          label: 'Расписание',
          icon: 'schedule',
          route: '/dashboard/student/schedule',
          color: '#0077FF',
        },
        {
          id: 'projects',
          label: 'Проекты',
          icon: 'projects',
          route: '/dashboard/student/projects',
          color: '#0077FF',
        },
        {
          id: 'library',
          label: 'Библиотека',
          icon: 'library',
          route: '/dashboard/student/library',
          color: '#0077FF',
        },
      ];

    case 'staff':
      return [
        {
          id: 'travel',
          label: 'Командировки',
          icon: 'business-trips',
          route: '/dashboard/staff/travel',
          color: '#0077FF',
        },
        {
          id: 'vacations',
          label: 'Отпуска',
          icon: 'vacations',
          route: '/dashboard/staff/vacations',
          color: '#0077FF',
        },
        {
          id: 'office',
          label: 'Офис и HR',
          icon: 'office',
          route: '/dashboard/staff/office',
          color: '#0077FF',
        },
      ];

    case 'admin':
      return [
        {
          id: 'metrics',
          label: 'Метрики',
          icon: 'academic-metrics',
          route: '/dashboard/admin',
          color: '#0077FF',
        },
        {
          id: 'news',
          label: 'Новости',
          icon: 'news-aggregator',
          route: '/dashboard/admin',
          color: '#0077FF',
        },
      ];

    default:
      return [];
  }
}

